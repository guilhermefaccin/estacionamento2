
const API_BASE = "http://127.0.0.1:8000";

// Dados do usuário autenticado
const auth = {
  token: null,
  usuario: null
};

const API = {
  usuarios: "/usuarios",
  clientes: "/clientes",
  veiculos: "/veiculos",
  marcas: "/marcas",
  vagas: "/vagas",
  tarifas: "/tarifas",
  contratos: "/contratos-mensais",
  estacionamentos: "/estacionamentos"
};

const $ = (id) => document.getElementById(id);

const state = {
  page: "inicio",
  editing: {},
  data: {}
};

const titles = {
  inicio: "Visão geral",
  estacionamentos: "Entrada e saída",
  usuarios: "Usuários",
  clientes: "Clientes",
  veiculos: "Veículos",
  marcas: "Marcas",
  vagas: "Vagas",
  tarifas: "Tarifas",
  contratos: "Contratos mensais"
};

// ========================================
// AUTENTICAÇÃO
// ========================================

// Decodifica o conteúdo de um token JWT
function decodificarToken(token) {
  const partes = token.split(".");

  if (partes.length !== 3) {
    throw new Error("Token inválido.");
  }

  let base64 = partes[1]
    .replace(/-/g, "+")
    .replace(/_/g, "/");

  base64 += "=".repeat((4 - base64.length % 4) % 4);

  const binario = atob(base64);

  const bytes = Uint8Array.from(
    binario,
    caractere => caractere.charCodeAt(0)
  );

  return JSON.parse(new TextDecoder().decode(bytes));
}

// Realiza o login no sistema
$("form-login").addEventListener("submit", async event => {
  event.preventDefault();

  const email = $("login-email").value.trim();
  const senha = $("login-senha").value;
  const botao = $("btn-login");
  const erro = $("login-erro");

  erro.hidden = true;
  botao.disabled = true;
  botao.textContent = "Entrando...";

  try {
    const response = await fetch(`${API_BASE}/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ email, senha })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        typeof data.detail === "string"
          ? data.detail
          : "E-mail ou senha inválidos."
      );
    }

    auth.token = data.access_token;

    const payload = decodificarToken(auth.token);

    if (
      !payload.sub ||
      !payload.perfil ||
      !payload.exp ||
      payload.exp * 1000 <= Date.now()
    ) {
      throw new Error("O servidor retornou um token inválido.");
    }

    auth.usuario = {
      id_usuario: Number(payload.sub),
      perfil: payload.perfil
    };

    sessionStorage.setItem("token", auth.token);
    sessionStorage.setItem(
      "usuario",
      JSON.stringify(auth.usuario)
    );

    $("login-screen").hidden = true;
    $("app-container").hidden = false;

    $("form-login").reset();

    showAlert("Login realizado com sucesso!");

    await boot();

  } catch (error) {
    auth.token = null;
    auth.usuario = null;

    erro.textContent = error.message;
    erro.hidden = false;

  } finally {
    botao.disabled = false;
    botao.textContent = "Entrar no sistema";
  }
});

// Recupera a sessão salva no navegador
function recuperarSessao() {
  const token = sessionStorage.getItem("token");
  const usuario = sessionStorage.getItem("usuario");

  if (!token || !usuario) {
    return false;
  }

  try {
    const payload = decodificarToken(token);

    if (
      !payload.sub ||
      !payload.perfil ||
      !payload.exp ||
      payload.exp * 1000 <= Date.now()
    ) {
      throw new Error("Token expirado ou inválido.");
    }

    auth.token = token;
    auth.usuario = {
      id_usuario: Number(payload.sub),
      perfil: payload.perfil
    };

    $("login-screen").hidden = true;
    $("app-container").hidden = false;

    return true;

  } catch {
    auth.token = null;
    auth.usuario = null;

    sessionStorage.removeItem("token");
    sessionStorage.removeItem("usuario");

    return false;
  }
}
// ========================================
// LOGOUT
// ========================================

function logout() {
  // Limpa os dados de autenticação
  auth.token = null;
  auth.usuario = null;

  // Remove a sessão armazenada
  sessionStorage.removeItem("token");
  sessionStorage.removeItem("usuario");

  // Esconde o painel
  $("app-container").hidden = true;

  // Exibe a tela de login
  $("login-screen").hidden = false;

  // Limpa os campos do login
  $("form-login").reset();

  // Esconde mensagens de erro
  $("login-erro").hidden = true;

  // Retorna o foco para o e-mail
  $("login-email").focus();

  showAlert("Você saiu do sistema.");
}

// Evento do botão Sair
$("btn-logout").addEventListener("click", () => {
  if (confirm("Deseja realmente sair do sistema?")) {
    logout();
  }
});
// ========================================
// ALERTAS
// ========================================

function showAlert(message, error = false) {
  const el = $("alerta");
  el.textContent = message;
  el.hidden = false;
  el.className = "alert " + (error ? "error" : "success");

  window.clearTimeout(showAlert.timer);

  showAlert.timer = window.setTimeout(() => {
    el.hidden = true;
  }, 6500);
}

// ========================================
// CONEXÃO COM A API
// ========================================

async function api(path, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {})
  };

  // Envia o JWT automaticamente
  if (auth.token) {
    headers.Authorization = `Bearer ${auth.token}`;
  }

  const response = await fetch(API_BASE + path, {
    ...options,
    headers
  });

  if (!response.ok) {
    let message = `Erro HTTP ${response.status}`;

    try {
      const body = await response.json();

      message = typeof body.detail === "string"
        ? body.detail
        : JSON.stringify(body.detail || body);
    } catch {}

    throw new Error(message);
  }

  if (response.status === 204) return null;

  const type = response.headers.get("content-type") || "";

  return type.includes("application/json")
    ? response.json()
    : null;
}

// ========================================
// FUNÇÕES AUXILIARES
// ========================================

function esc(value) {
  return String(value ?? "").replace(/[&<>"']/g, c => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;"
  }[c]));
}

function money(value) {
  return Number(value || 0).toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL"
  });
}

function dateTime(value) {
  if (!value) return "—";

  const date = new Date(String(value).replace(" ", "T"));

  return Number.isNaN(date.getTime())
    ? value
    : date.toLocaleString("pt-BR");
}

function dateOnly(value) {
  if (!value) return "—";

  const date = new Date(String(value).slice(0, 10) + "T12:00:00");

  return Number.isNaN(date.getTime())
    ? value
    : date.toLocaleDateString("pt-BR");
}

function badge(value) {
  const safe = esc(value || "—");

  return `<span class="badge badge-${safe.toLowerCase()}">${safe}</span>`;
}

function actions(id, module) {
  return `
    <button class="btn btn-small btn-outline"
      data-edit="${module}" data-id="${esc(id)}">
      Editar
    </button>
    <button class="btn btn-small btn-danger"
      data-disable="${module}" data-id="${esc(id)}">
      ${module === "contratos" ? "Encerrar" : "Desativar"}
    </button>
  `;
}

// ========================================
// NAVEGAÇÃO
// ========================================

function navigate(page) {
  if (!titles[page]) return;

  state.page = page;

  document.querySelectorAll(".page").forEach(element => {
    element.classList.toggle(
      "active",
      element.id === `page-${page}`
    );
  });

  document.querySelectorAll(".nav-link").forEach(button => {
    button.classList.toggle(
      "active",
      button.dataset.page === page
    );
  });

  $("page-title").textContent = titles[page];

  if (page === "inicio") loadDashboard();

  if (page === "estacionamentos") {
    loadParking();
    loadSelects();
  }

  if ([
    "usuarios",
    "clientes",
    "veiculos",
    "marcas",
    "vagas",
    "tarifas",
    "contratos"
  ].includes(page)) {
    loadModule(page);
  }

  if (["veiculos", "contratos"].includes(page)) {
    loadSelects();
  }
}

document.querySelectorAll("[data-page]").forEach(button => {
  button.addEventListener("click", () => {
    navigate(button.dataset.page);
  });
});

document.querySelectorAll("[data-go]").forEach(button => {
  button.addEventListener("click", () => {
    navigate(button.dataset.go);
  });
});

document.querySelectorAll("[data-refresh]").forEach(button => {
  button.addEventListener("click", () => {
    loadModule(button.dataset.refresh);
  });
});

$("today").textContent = new Date().toLocaleDateString("pt-BR", {
  weekday: "short",
  day: "2-digit",
  month: "short",
  year: "numeric"
});

// ========================================
// CONFIGURAÇÕES DOS CADASTROS
// ========================================

const configs = {
  usuarios: {
    path: API.usuarios,
    id: "id_usuario",
    list: "lista-usuarios",
    fields: ["id_usuario", "nome", "cpf", "email"],
    cols: ["ID", "Nome", "CPF", "E-mail"],
    form: "form-usuarios",
    title: "usuarios-form-title",
    inputs: ["u-nome", "u-cpf", "u-email"],

    payload: () => ({
      nome: $("u-nome").value.trim(),
      cpf: $("u-cpf").value.trim(),
      email: $("u-email").value.trim()
    }),

    makeEdit: row => {
      $("u-nome").value = row.nome || "";
      $("u-cpf").value = row.cpf || "";
      $("u-email").value = row.email || "";
    }
  },

  clientes: {
    path: API.clientes,
    id: "id_cliente",
    list: "lista-clientes",
    fields: ["id_cliente", "nome", "cpf_cnpj", "telefone", "email"],
    cols: ["ID", "Nome", "CPF/CNPJ", "Telefone", "E-mail"],
    form: "form-clientes",
    title: "clientes-form-title",
    inputs: ["c-nome", "c-documento", "c-telefone", "c-email", "c-usuario"],

    payload: () => ({
      nome: $("c-nome").value.trim(),
      cpf_cnpj: $("c-documento").value.trim(),
      telefone: $("c-telefone").value.trim() || null,
      email: $("c-email").value.trim() || null,
      id_usuario_cadastro: 1
    }),

    makeEdit: row => {
      $("c-nome").value = row.nome || "";
      $("c-documento").value = row.cpf_cnpj || "";
      $("c-telefone").value = row.telefone || "";
      $("c-email").value = row.email || "";
    }
  },

  veiculos: {
    path: API.veiculos,
    id: "id_veiculo",
    list: "lista-veiculos",
    fields: ["id_veiculo", "placa", "modelo", "id_cliente", "id_marca"],
    cols: ["ID", "Placa", "Modelo", "Cliente", "Marca"],
    form: "form-veiculos",
    title: "veiculos-form-title",
    inputs: ["v-cliente", "v-marca", "v-placa", "v-modelo", "v-cor", "v-usuario"],

    payload: () => ({
      id_cliente: Number($("v-cliente").value),
      id_marca: Number($("v-marca").value),
      placa: $("v-placa").value.trim().toUpperCase(),
      modelo: $("v-modelo").value.trim(),
      cor: $("v-cor").value.trim() || null,
      id_usuario_cadastro: 1
    }),

    makeEdit: row => {
      $("v-cliente").value = row.id_cliente || "";
      $("v-marca").value = row.id_marca || "";
      $("v-placa").value = row.placa || "";
      $("v-modelo").value = row.modelo || "";
      $("v-cor").value = row.cor || "";
    }
  },

  marcas: {
    path: API.marcas,
    id: "id_marca",
    list: "lista-marcas",
    fields: ["id_marca", "nome"],
    cols: ["ID", "Marca"],
    form: "form-marcas",
    title: "marcas-form-title",
    inputs: ["m-nome", "m-usuario"],

    payload: () => ({
      nome: $("m-nome").value.trim(),
      id_usuario_cadastro: 1
    }),

    makeEdit: row => {
      $("m-nome").value = row.nome || "";
    }
  },

  vagas: {
    path: API.vagas,
    id: "id_vaga",
    list: "lista-vagas",
    fields: ["id_vaga", "numero_vaga", "tipo_uso", "status"],
    cols: ["ID", "Número", "Tipo de uso", "Status"],
    form: "form-vagas",
    title: "vagas-form-title",
    inputs: ["vaga-numero", "vaga-tipo-uso"],

    payload: () => ({
      numero_vaga: $("vaga-numero").value.trim(),
      tipo_vaga: "carro",
      tipo_uso: $("vaga-tipo-uso").value
    }),

    makeEdit: row => {
      $("vaga-numero").value = row.numero_vaga || "";
      $("vaga-tipo-uso").value = row.tipo_uso || "rotativa";
    }
  },

  tarifas: {
    path: API.tarifas,
    id: "id_tarifa",
    list: "lista-tarifas",
    fields: ["id_tarifa", "nome", "modalidade", "valor", "intervalo_minutos"],
    cols: ["ID", "Nome", "Modalidade", "Valor", "Intervalo"],
    form: "form-tarifas",
    title: "tarifas-form-title",
    inputs: ["t-nome", "t-modalidade", "t-valor", "t-intervalo", "t-inicio", "t-fim"],

    payload: () => ({
      nome: $("t-nome").value.trim(),
      modalidade: $("t-modalidade").value,
      valor: Number($("t-valor").value),
      intervalo_minutos: $("t-modalidade").value === "horista"
        ? Number($("t-intervalo").value)
        : null,
      ...(
        $("t-inicio").value
          ? {
              data_inicio_vigencia:
                $("t-inicio").value.replace("T", " ") + ":00"
            }
          : {}
      ),
      data_fim_vigencia: $("t-fim").value
        ? $("t-fim").value.replace("T", " ") + ":00"
        : null
    }),

    makeEdit: row => {
      $("t-nome").value = row.nome || "";
      $("t-modalidade").value = row.modalidade || "horista";
      $("t-valor").value = row.valor ?? "";
      $("t-intervalo").value = row.intervalo_minutos ?? "";

      $("t-inicio").value = row.data_inicio_vigencia
        ? String(row.data_inicio_vigencia).replace(" ", "T").slice(0, 16)
        : "";

      $("t-fim").value = row.data_fim_vigencia
        ? String(row.data_fim_vigencia).replace(" ", "T").slice(0, 16)
        : "";
    }
  },

  contratos: {
    path: API.contratos,
    id: "id_contrato",
    list: "lista-contratos",
    fields: ["id_contrato", "id_cliente", "id_vaga", "data_inicio", "valor_mensal", "status"],
    cols: ["ID", "Cliente", "Vaga", "Início", "Valor mensal", "Status"],
    form: "form-contratos",
    title: "contratos-form-title",
    inputs: ["ct-cliente", "ct-vaga", "ct-tarifa", "ct-inicio", "ct-fim", "ct-vencimento", "ct-valor", "ct-usuario"],

    payload: () => ({
      id_cliente: Number($("ct-cliente").value),
      id_vaga: $("ct-vaga").value
        ? Number($("ct-vaga").value)
        : null,
      id_tarifa: Number($("ct-tarifa").value),
      data_inicio: $("ct-inicio").value,
      data_fim: $("ct-fim").value || null,
      dia_vencimento: Number($("ct-vencimento").value),
      valor_mensal: Number($("ct-valor").value),
      id_usuario_cadastro: 1
    }),

    makeEdit: row => {
      $("ct-cliente").value = row.id_cliente || "";
      $("ct-vaga").value = row.id_vaga || "";
      $("ct-tarifa").value = row.id_tarifa || "";
      $("ct-inicio").value = String(row.data_inicio || "").slice(0, 10);
      $("ct-fim").value = String(row.data_fim || "").slice(0, 10);
      $("ct-vencimento").value = row.dia_vencimento || 10;
      $("ct-valor").value = row.valor_mensal ?? "";
    }
  }
};

// ========================================
// FORMULÁRIOS
// ========================================

function resetForm(module) {
  const config = configs[module];
  if (!config) return;

  $(config.form).reset();
  state.editing[module] = null;

  const names = {
    contratos: "contrato mensal",
    usuarios: "usuário",
    veiculos: "veículo",
    vagas: "vaga",
    tarifas: "tarifa",
    marcas: "marca",
    clientes: "cliente"
  };

  $(config.title).textContent =
    `Cadastrar ${names[module] || module}`;

  const cancelIds = {
    usuarios: "u-cancelar",
    clientes: "c-cancelar",
    veiculos: "v-cancelar",
    marcas: "m-cancelar",
    vagas: "vaga-cancelar",
    tarifas: "t-cancelar",
    contratos: "ct-cancelar"
  };

  const cancel = $(cancelIds[module]);
  if (cancel) cancel.hidden = true;

  const userIds = {
    clientes: "c-usuario",
    veiculos: "v-usuario",
    marcas: "m-usuario",
    contratos: "ct-usuario"
  };

  if (userIds[module]) {
    $(userIds[module]).value = "1";
  }
}

// ========================================
// TABELAS
// ========================================

function renderCell(module, key, value, row) {
  if (key === "valor" || key === "valor_mensal") {
    return money(value);
  }

  if (key === "data_inicio") {
    return dateOnly(value);
  }

  if (
    key === "status" ||
    key === "tipo_uso" ||
    key === "modalidade"
  ) {
    return badge(value);
  }

  if (key === "id_cliente") {
    return esc(
      (state.data.clientes || []).find(
        x => x.id_cliente === value
      )?.nome || value || "—"
    );
  }

  if (key === "id_marca") {
    return esc(
      (state.data.marcas || []).find(
        x => x.id_marca === value
      )?.nome || value || "—"
    );
  }

  if (key === "id_vaga") {
    return esc(
      (state.data.vagas || []).find(
        x => x.id_vaga === value
      )?.numero_vaga || value || "—"
    );
  }

  return esc(value ?? "—");
}

async function loadModule(module) {
  const config = configs[module];
  if (!config) return;

  const body = $(config.list);
  if (!body) return;

  body.innerHTML = `
    <tr>
      <td colspan="${config.fields.length + 1}" class="empty">
        Carregando...
      </td>
    </tr>
  `;

  try {
    let data = await api(config.path);

    if (!Array.isArray(data)) {
      data = data?.items || data?.dados || [];
    }

    state.data[module] = data;
    body.innerHTML = "";

    if (!data.length) {
      body.innerHTML = `
        <tr>
          <td colspan="${config.fields.length + 1}" class="empty">
            Nenhum registro encontrado.
          </td>
        </tr>
      `;
      return;
    }

    data.forEach(row => {
      const tr = document.createElement("tr");

      config.fields.forEach(field => {
        const td = document.createElement("td");

        td.innerHTML = renderCell(
          module,
          field,
          row[field],
          row
        );

        tr.appendChild(td);
      });

      const td = document.createElement("td");
      td.innerHTML = actions(row[config.id], module);

      tr.appendChild(td);
      body.appendChild(tr);
    });

  } catch (error) {
    body.innerHTML = `
      <tr>
        <td colspan="${config.fields.length + 1}" class="empty">
          Não foi possível carregar: ${esc(error.message)}
        </td>
      </tr>
    `;
  }
}

// ========================================
// CADASTRAR E EDITAR
// ========================================

Object.entries(configs).forEach(([module, config]) => {
  const form = $(config.form);
  if (!form) return;

  form.addEventListener("submit", async event => {
    event.preventDefault();

    try {
      const id = state.editing[module];
      const payload = config.payload();

      let url;

      if (module === "contratos") {
        const idUsuario = "1";

        url = id
          ? `${config.path}/${id}?id_usuario=${idUsuario}`
          : `${config.path}?id_usuario=${idUsuario}`;
      } else {
        url = id
          ? `${config.path}/${id}`
          : config.path;
      }

      await api(url, {
        method: id ? "PUT" : "POST",
        body: JSON.stringify(payload)
      });

      showAlert(
        `${module[0].toUpperCase() + module.slice(1)} ${
          id ? "atualizado" : "cadastrado"
        } com sucesso.`
      );

      resetForm(module);
      await loadModule(module);
      await loadSelects();

      if (module === "estacionamentos") {
        await loadParking();
      }

    } catch (error) {
      showAlert(error.message, true);
    }
  });

  const cancelIds = {
    usuarios: "u-cancelar",
    clientes: "c-cancelar",
    veiculos: "v-cancelar",
    marcas: "m-cancelar",
    vagas: "vaga-cancelar",
    tarifas: "t-cancelar",
    contratos: "ct-cancelar"
  };

  const cancel = $(cancelIds[module]);

  if (cancel) {
    cancel.addEventListener("click", () => {
      resetForm(module);
    });
  }
});

// ========================================
// EDITAR E DESATIVAR REGISTROS
// ========================================

document.addEventListener("click", async event => {
  const edit = event.target.closest("[data-edit]");
  const disable = event.target.closest("[data-disable]");

  if (edit) {
    const module = edit.dataset.edit;
    const config = configs[module];

    const row = (state.data[module] || []).find(
      item => String(item[config.id]) === edit.dataset.id
    );

    if (!row) return;

    state.editing[module] = row[config.id];

    config.makeEdit(row);

    $(config.title).textContent =
      `Editar registro #${row[config.id]}`;

    const cancelIds = {
      usuarios: "u-cancelar",
      clientes: "c-cancelar",
      veiculos: "v-cancelar",
      marcas: "m-cancelar",
      vagas: "vaga-cancelar",
      tarifas: "t-cancelar",
      contratos: "ct-cancelar"
    };

    const cancel = $(cancelIds[module]);

    if (cancel) cancel.hidden = false;

    window.scrollTo({
      top: 0,
      behavior: "smooth"
    });
  }

  if (disable) {
    const module = disable.dataset.disable;
    const config = configs[module];

    if (!config) return;

    const action = module === "contratos"
      ? "encerrar"
      : "desativar";

    if (
      !confirm(
        `Deseja ${action === "encerrar" ? "encerrar" : "desativar"} o registro #${disable.dataset.id}?`
      )
    ) {
      return;
    }

    try {
      let url;

      if (module === "contratos") {
        url = `${config.path}/${disable.dataset.id}/encerrar?id_usuario=1`;
      } else {
        url = `${config.path}/${disable.dataset.id}/desativar`;
      }

      await api(url, { method: "PATCH" });

      showAlert(
        module === "contratos"
          ? "Contrato encerrado com sucesso."
          : "Registro desativado com sucesso."
      );

      await loadModule(module);
      await loadSelects();

    } catch (error) {
      showAlert(
        `Não foi possível concluir a operação: ${error.message}`,
        true
      );
    }
  }
});

// ========================================
// LISTAS DE SELEÇÃO
// ========================================

async function loadSelect(id, path, labelFn, placeholder = "Selecione") {
  const element = $(id);
  if (!element) return;

  const previous = element.value;

  try {
    let rows = await api(path);

    if (!Array.isArray(rows)) {
      rows = rows?.items || [];
    }

    element.innerHTML =
      `<option value="">${placeholder}</option>` +
      rows.map(row => {
        const idValue =
          row.id_veiculo ??
          row.id_cliente ??
          row.id_marca ??
          row.id_vaga ??
          row.id_tarifa ??
          row.id_contrato;

        return `
          <option value="${esc(idValue)}">
            ${esc(labelFn(row))}
          </option>
        `;
      }).join("");

    if (previous) {
      element.value = previous;
    }

  } catch {
    element.innerHTML = `
      <option value="">Não foi possível carregar</option>
    `;
  }
}

async function loadSelects() {
  await Promise.all([
    loadSelect(
      "entrada-veiculo",
      API.veiculos,
      row => `${row.placa} — ${row.modelo}`
    ),

    loadSelect(
      "entrada-vaga",
      API.vagas,
      row => `${row.numero_vaga} (${row.status})`,
      "Selecione uma vaga"
    ),

    loadSelect(
      "entrada-tarifa",
      API.tarifas,
      row => `${row.nome} — ${money(row.valor)}`
    ),

    loadSelect(
      "v-cliente",
      API.clientes,
      row => row.nome
    ),

    loadSelect(
      "v-marca",
      API.marcas,
      row => row.nome
    ),

    loadSelect(
      "ct-cliente",
      API.clientes,
      row => row.nome
    ),

    loadSelect(
      "ct-vaga",
      API.vagas,
      row => row.numero_vaga,
      "Sem vaga definida"
    ),

    loadSelect(
      "ct-tarifa",
      API.tarifas,
      row => `${row.nome} — ${money(row.valor)}`
    )
  ]);

  const vaga = $("entrada-vaga");

  if (vaga) {
    [...vaga.options].forEach(option => {
      if (!option.value) return;

      const row = (state.data.vagas || []).find(
        item => String(item.id_vaga) === option.value
      );

      if (
        row &&
        (
          row.status !== "livre" ||
          row.tipo_uso !== "rotativa" ||
          row.ativo === false
        )
      ) {
        option.remove();
      }
    });
  }

  const tarifa = $("entrada-tarifa");

  if (tarifa) {
    [...tarifa.options].forEach(option => {
      if (!option.value) return;

      const row = (state.data.tarifas || []).find(
        item => String(item.id_tarifa) === option.value
      );

      if (
        row &&
        (
          row.modalidade !== "horista" ||
          row.ativo === false
        )
      ) {
        option.remove();
      }
    });
  }
}

// ========================================
// REGISTRAR ENTRADA
// ========================================

$("form-entrada").addEventListener("submit", async event => {
  event.preventDefault();

  try {
    const body = {
      id_veiculo: Number($("entrada-veiculo").value),
      id_vaga: Number($("entrada-vaga").value),
      id_tarifa: Number($("entrada-tarifa").value)
    };

    await api(
      `${API.estacionamentos}/entrada?id_usuario=1`,
      {
        method: "POST",
        body: JSON.stringify(body)
      }
    );

    showAlert("Entrada registrada com sucesso.");

    $("form-entrada").reset();
    $("entrada-usuario").value = "1";

    await loadParking();
    await loadSelects();
    await loadModule("vagas");

  } catch (error) {
    showAlert(error.message, true);
  }
});

$("btn-atualizar-abertos").addEventListener(
  "click",
  loadParking
);

// ========================================
// ESTACIONAMENTOS ABERTOS
// ========================================

async function loadParking() {
  const body = $("lista-abertos");
  if (!body) return;

  body.innerHTML = `
    <tr>
      <td colspan="6" class="empty">Carregando...</td>
    </tr>
  `;

  try {
    let rows = await api(`${API.estacionamentos}/abertos`);

    if (!Array.isArray(rows)) rows = [];

    state.data.estacionamentos = rows;

    $("abertos-count").textContent =
      `${rows.length} aberto${rows.length === 1 ? "" : "s"}`;

    body.innerHTML = "";

    if (!rows.length) {
      body.innerHTML = `
        <tr>
          <td colspan="6" class="empty">
            Nenhum estacionamento aberto.
          </td>
        </tr>
      `;
      return;
    }

    rows.forEach(row => {
      const vehicle = (state.data.veiculos || []).find(
        item => item.id_veiculo === row.id_veiculo
      );

      const space = (state.data.vagas || []).find(
        item => item.id_vaga === row.id_vaga
      );

      const tariff = (state.data.tarifas || []).find(
        item => item.id_tarifa === row.id_tarifa
      );

      const tr = document.createElement("tr");

      [
        row.id_estacionamento,
        vehicle
          ? `${vehicle.placa} — ${vehicle.modelo}`
          : `Veículo #${row.id_veiculo}`,
        space?.numero_vaga || `Vaga #${row.id_vaga}`,
        dateTime(row.data_hora_entrada),
        tariff?.nome || `Tarifa #${row.id_tarifa || "—"}`
      ].forEach(value => {
        const td = document.createElement("td");
        td.textContent = value ?? "—";
        tr.appendChild(td);
      });

      const td = document.createElement("td");
      const button = document.createElement("button");

      button.className = "btn btn-small btn-primary";
      button.textContent = "Registrar saída";

      button.addEventListener("click", async () => {
        if (
          !confirm(
            `Registrar saída do estacionamento #${row.id_estacionamento}?`
          )
        ) {
          return;
        }

        try {
          const result = await api(
            `${API.estacionamentos}/${row.id_estacionamento}/saida?id_usuario=1`,
            { method: "PATCH" }
          );

          showAlert(
            `Saída registrada. Valor calculado: ${money(result.valor_calculado)}.`
          );

          await loadParking();
          await loadSelects();
          await loadModule("vagas");

        } catch (error) {
          showAlert(error.message, true);
        }
      });

      td.appendChild(button);
      tr.appendChild(td);
      body.appendChild(tr);
    });

  } catch (error) {
    body.innerHTML = `
      <tr>
        <td colspan="6" class="empty">
          Não foi possível carregar estacionamentos:
          ${esc(error.message)}
        </td>
      </tr>
    `;
  }
}

// ========================================
// PAINEL PRINCIPAL
// ========================================

async function loadDashboard() {
  const read = async path => {
    try {
      const data = await api(path);

      return Array.isArray(data)
        ? data.length
        : 0;

    } catch {
      return "—";
    }
  };

  const [open, spaces, users, vehicles] = await Promise.all([
    read(`${API.estacionamentos}/abertos`),
    read(API.vagas),
    read(API.usuarios),
    read(API.veiculos)
  ]);

  $("stat-abertos").textContent = open;
  $("stat-vagas").textContent = spaces;
  $("stat-usuarios").textContent = users;
  $("stat-veiculos").textContent = vehicles;

  try {
    const [
      vehiclesData,
      spacesData,
      tariffsData,
      contractsData,
      clientsData
    ] = await Promise.all([
      api(API.veiculos),
      api(API.vagas),
      api(API.tarifas),
      api(API.contratos),
      api(API.clientes)
    ]);

    state.data.veiculos = Array.isArray(vehiclesData)
      ? vehiclesData
      : [];

    state.data.vagas = Array.isArray(spacesData)
      ? spacesData
      : [];

    state.data.tarifas = Array.isArray(tariffsData)
      ? tariffsData
      : [];

    state.data.contratos = Array.isArray(contractsData)
      ? contractsData
      : [];

    state.data.clientes = Array.isArray(clientsData)
      ? clientsData
      : [];

  } catch {}
}

// ========================================
// STATUS DA API
// ========================================

async function checkApi() {
  try {
    await api("/status");
    $("api-status").textContent = "online";

  } catch {
    $("api-status").textContent = "API configurada";
  }
}

// ========================================
// INICIALIZAÇÃO
// ========================================

async function boot() {
  await checkApi();
  await loadDashboard();
  await loadSelects();
  await loadModule("usuarios");
}

// Só abre o painel quando existir uma sessão válida
if (recuperarSessao()) {
  boot();

} else {
  $("login-screen").hidden = false;
  $("app-container").hidden = true;
}
