const form = document.querySelector("#search-form");
const searchInput = document.querySelector("#search-input");
const searchButton = document.querySelector(".search-button");
const resultsGrid = document.querySelector("#results-grid");
const resultsTitle = document.querySelector("#results-title");
const resultsCount = document.querySelector("#results-count");
const emptyState = document.querySelector("#empty-state");
const dialog = document.querySelector("#recipe-dialog");
const dialogContent = document.querySelector("#dialog-content");
const toast = document.querySelector("#toast");

let searchGeneration = 0;
let detailGeneration = 0;
let toastTimer;

const sourceNames = {
  kaggle: "Kaggle",
  themealdb: "TheMealDB",
};

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("visible");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove("visible"), 3600);
}

function setLoading(isLoading) {
  searchButton.disabled = isLoading;
  searchButton.querySelector("span:first-child").textContent = isLoading ? "Buscando..." : "Buscar recetas";
}

function setSkeletons() {
  resultsGrid.replaceChildren(...Array.from({ length: 6 }, () => {
    const skeleton = document.createElement("div");
    skeleton.className = "skeleton";
    return skeleton;
  }));
  emptyState.classList.add("hidden");
}

async function requestJson(url, options) {
  let response;
  try {
    response = await fetch(url, options);
  } catch {
    throw new Error("No se pudo conectar con el backend. Comprueba que sigue activo.");
  }
  let payload;
  try {
    payload = await response.json();
  } catch {
    throw new Error("El backend devolvió una respuesta que no se pudo leer.");
  }
  if (!response.ok) {
    throw new Error(payload.detail || `Error del servidor (${response.status}).`);
  }
  return payload;
}

async function searchRecipes(query = searchInput.value.trim()) {
  const cleanQuery = query.trim();
  if (!cleanQuery) {
    showToast("Escribe el nombre de una receta para empezar.");
    searchInput.focus();
    return;
  }

  searchInput.value = cleanQuery;
  const generation = ++searchGeneration;
  resultsTitle.textContent = `Resultados para «${cleanQuery}»`;
  resultsCount.textContent = "";
  setLoading(true);
  setSkeletons();

  try {
    const params = new URLSearchParams({ q: cleanQuery });
    const recipes = await requestJson(`/api/recipes/search?${params}`);
    if (generation !== searchGeneration) return;
    renderResults(recipes);
  } catch (error) {
    if (generation !== searchGeneration) return;
    resultsGrid.replaceChildren();
    emptyState.classList.remove("hidden");
    emptyState.querySelector("p").textContent = error.message;
    showToast(error.message);
  } finally {
    if (generation === searchGeneration) setLoading(false);
  }
}

function renderResults(recipes) {
  resultsGrid.replaceChildren();
  resultsCount.textContent = `${recipes.length} ${recipes.length === 1 ? "receta" : "recetas"}`;
  if (!recipes.length) {
    emptyState.classList.remove("hidden");
    emptyState.querySelector("p").textContent = "No encontramos coincidencias. Prueba con otro nombre o ingrediente.";
    return;
  }
  emptyState.classList.add("hidden");

  recipes.forEach((recipe, index) => {
    const card = document.createElement("button");
    card.type = "button";
    card.className = "recipe-card";
    card.style.animationDelay = `${Math.min(index, 9) * 45}ms`;
    card.setAttribute("aria-label", `Ver receta ${recipe.name}`);

    const number = document.createElement("span");
    number.className = "card-index";
    number.textContent = String(index + 1).padStart(2, "0");

    const source = document.createElement("span");
    source.className = "card-source";
    source.textContent = sourceNames[recipe.source] || recipe.source;

    const title = document.createElement("h3");
    title.textContent = recipe.name;

    const meta = document.createElement("span");
    meta.className = "card-meta";
    const descriptor = recipe.category || recipe.area || (recipe.step_count ? `${recipe.step_count} pasos` : "Ver receta completa");
    meta.textContent = descriptor;

    const arrow = document.createElement("span");
    arrow.className = "card-arrow";
    arrow.setAttribute("aria-hidden", "true");
    arrow.textContent = "↗";

    card.append(number, source, title, meta, arrow);
    card.addEventListener("click", () => openRecipe(recipe.source, recipe.id));
    resultsGrid.append(card);
  });
}

function addSection(title, content) {
  const section = document.createElement("section");
  section.className = "dialog-section";
  const heading = document.createElement("h3");
  heading.textContent = title;
  section.append(heading, content);
  dialogContent.append(section);
}

function renderIngredients(ingredients) {
  const list = document.createElement("ul");
  list.className = "ingredient-list";
  ingredients.forEach((ingredient) => {
    const item = document.createElement("li");
    const name = document.createElement("span");
    name.className = "ingredient-name";
    name.textContent = ingredient.ingredient || "";
    const measure = document.createElement("span");
    measure.className = "ingredient-measure";
    measure.textContent = ingredient.measure_raw || "";
    item.append(name, measure);
    list.append(item);
  });
  return list;
}

function renderInstructions(recipe) {
  if (recipe.source === "kaggle") {
    const list = document.createElement("ol");
    list.className = "steps-list";
    recipe.steps.forEach((step) => {
      const item = document.createElement("li");
      item.textContent = step.instruction;
      list.append(item);
    });
    return list;
  }
  const instructions = document.createElement("p");
  instructions.className = "instruction-copy";
  instructions.textContent = recipe.instructions || "No hay instrucciones registradas.";
  return instructions;
}

function buildRecipeView(recipe, isTranslated = false, originalRecipe = recipe) {
  dialogContent.replaceChildren();

  const eyebrow = document.createElement("p");
  eyebrow.className = "dialog-eyebrow";
  eyebrow.textContent = `${sourceNames[recipe.source] || recipe.source} · ${isTranslated ? "Traducción automática" : "Receta del catálogo"}`;

  const title = document.createElement("h2");
  title.textContent = recipe.name || "Receta";

  const description = document.createElement("p");
  description.className = "dialog-description";
  description.textContent = [recipe.category, recipe.area].filter(Boolean).join(" · ");

  dialogContent.append(eyebrow, title);
  if (description.textContent) dialogContent.append(description);

  const actions = document.createElement("div");
  actions.className = "dialog-actions";
  const translateButton = document.createElement("button");
  translateButton.className = "action-button";
  translateButton.type = "button";
  translateButton.textContent = isTranslated ? "Traducir de nuevo" : "Traducir receta al español";
  translateButton.addEventListener("click", () => translateRecipe(originalRecipe));
  actions.append(translateButton);

  if (isTranslated) {
    const originalButton = document.createElement("button");
    originalButton.className = "action-button secondary";
    originalButton.type = "button";
    originalButton.textContent = "Ver original";
    originalButton.addEventListener("click", () => buildRecipeView(originalRecipe));
    actions.append(originalButton);
  }
  dialogContent.append(actions);

  if (recipe.ingredients?.length) addSection("Ingredientes registrados", renderIngredients(recipe.ingredients));
  if (recipe.steps?.length || recipe.instructions) addSection("Preparación", renderInstructions(recipe));

  if (recipe.source_url) {
    const link = document.createElement("a");
    link.className = "source-link";
    link.href = recipe.source_url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.textContent = "Ver fuente original ↗";
    dialogContent.append(link);
  }

  const note = document.createElement("p");
  note.className = "recipe-note";
  note.textContent = "La traducción es automática. Comprueba siempre los ingredientes y las instrucciones originales; los datos no garantizan información completa sobre alérgenos, cantidades, raciones o tiempos.";
  dialogContent.append(note);
}

async function openRecipe(source, recipeId) {
  const generation = ++detailGeneration;
  dialogContent.replaceChildren();
  const loading = document.createElement("p");
  loading.className = "dialog-description";
  loading.textContent = "Cargando receta...";
  dialogContent.append(loading);
  if (!dialog.open) dialog.showModal();

  try {
    const recipe = await requestJson(`/api/recipes/${encodeURIComponent(source)}/${encodeURIComponent(recipeId)}`);
    if (generation !== detailGeneration) return;
    buildRecipeView(recipe);
  } catch (error) {
    if (generation !== detailGeneration) return;
    dialogContent.replaceChildren();
    const message = document.createElement("p");
    message.className = "dialog-description";
    message.textContent = error.message;
    dialogContent.append(message);
    showToast(error.message);
  }
}

async function translateRecipe(recipe) {
  const textItems = [];
  const addText = (text) => {
    const index = textItems.length;
    textItems.push(text || "");
    return index;
  };
  const indexes = {
    name: addText(recipe.name),
    category: addText(recipe.category),
    area: addText(recipe.area),
    ingredients: (recipe.ingredients || []).map((ingredient) => ({
      ingredient: addText(ingredient.ingredient),
      measure: addText(ingredient.measure_raw),
    })),
    steps: (recipe.steps || []).map((step) => addText(step.instruction)),
    instructions: addText(recipe.instructions),
  };
  const translatableIndexes = textItems
    .map((text, index) => text.trim() ? index : -1)
    .filter((index) => index >= 0);
  if (!translatableIndexes.length) {
    showToast("Esta receta no contiene textos para traducir.");
    return;
  }

  const button = dialogContent.querySelector(".action-button");
  if (button) {
    button.disabled = true;
    button.textContent = "Traduciendo…";
  }
  showToast("Enviando el texto de esta receta a LibreTranslate…");

  try {
    const translatedTexts = [...textItems];
    for (let offset = 0; offset < translatableIndexes.length; offset += 25) {
      const batch = translatableIndexes.slice(offset, offset + 25);
      const result = await requestJson("/api/translate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ texts: batch.map((index) => textItems[index]) }),
      });
      if (!Array.isArray(result.translations) || result.translations.length !== batch.length) {
        throw new Error("El servicio devolvió un resultado de traducción incompleto.");
      }
      batch.forEach((textIndex, resultIndex) => {
        translatedTexts[textIndex] = result.translations[resultIndex];
      });
    }

    const translatedAt = (index, original) =>
      textItems[index].trim() ? translatedTexts[index] : original;
    const translatedRecipe = {
      ...recipe,
      name: translatedAt(indexes.name, recipe.name),
      category: translatedAt(indexes.category, recipe.category),
      area: translatedAt(indexes.area, recipe.area),
      ingredients: (recipe.ingredients || []).map((ingredient, ingredientIndex) => ({
        ...ingredient,
        ingredient: translatedAt(
          indexes.ingredients[ingredientIndex].ingredient,
          ingredient.ingredient,
        ),
        measure_raw: translatedAt(
          indexes.ingredients[ingredientIndex].measure,
          ingredient.measure_raw,
        ),
      })),
      steps: (recipe.steps || []).map((step, stepIndex) => ({
        ...step,
        instruction: translatedAt(
          indexes.steps[stepIndex],
          step.instruction,
        ),
      })),
      instructions: translatedAt(indexes.instructions, recipe.instructions),
    };
    buildRecipeView(translatedRecipe, true, recipe);
    showToast("Receta traducida al español.");
  } catch (error) {
    showToast(error.message);
    if (button?.isConnected) {
      button.disabled = false;
      button.textContent = "Reintentar traducción";
    }
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  searchRecipes();
});

document.querySelectorAll(".hint-chip").forEach((button) => {
  button.addEventListener("click", () => searchRecipes(button.dataset.query));
});

document.querySelector("#dialog-close").addEventListener("click", () => dialog.close());
dialog.addEventListener("click", (event) => {
  if (event.target === dialog) dialog.close();
});
