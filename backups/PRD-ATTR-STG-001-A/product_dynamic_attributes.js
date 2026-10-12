(function () {
  "use strict";

  const categoryField = document.getElementById("id_category");
  const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]')?.value || "";
  let allowedAttributes = null;

  async function loadAttributes() {
    if (!categoryField || !categoryField.value) {
      allowedAttributes = null;
      return;
    }
    try {
      const response = await fetch("/products/admin-attributes/?category=" + encodeURIComponent(categoryField.value), {
        headers: { "X-CSRFToken": csrfToken, "X-Requested-With": "XMLHttpRequest" }
      });
      if (!response.ok) return;
      const data = await response.json();
      allowedAttributes = data.results || [];
      document.querySelectorAll('select[name$="-attribute"]').forEach(function (select) {
        if (!select.closest(".dynamic-attribute-row") && !select.id.includes("attribute_values")) return;
        const current = select.value;
        const original = select.dataset.originalOptions;
        if (!original) select.dataset.originalOptions = Array.from(select.options).map(o => JSON.stringify({value:o.value,text:o.text})).join("|");
        const allOptions = (select.dataset.originalOptions || "").split("|").filter(Boolean).map(s => JSON.parse(s));
        const allowedIds = new Set(allowedAttributes.map(a => String(a.id)));
        const empty = allOptions.find(o => !o.value) || {value:"",text:"---------"};
        const valid = allOptions.filter(o => allowedIds.has(String(o.value)));
        select.replaceChildren();
        [empty, ...valid].forEach(o => select.add(new Option(o.text, o.value)));
        if (allowedIds.has(String(current))) select.value = current;
        if (select.value) attachAutocomplete(select);
      });
    } catch (error) {
      console.warn("Could not load dynamic product attributes.", error);
    }
  }

  async function attachAutocomplete(attributeSelect) {
    const row = attributeSelect.closest("tr") || attributeSelect.parentElement;
    const textInput = row?.querySelector('input[name$="-value_text"], textarea[name$="-value_text"]');
    if (!textInput) return;
    const attributeId = attributeSelect.value;
    if (!attributeId) return;
    const listId = "attribute-values-" + attributeSelect.id.replace(/[^a-zA-Z0-9_-]/g, "-");
    let datalist = document.getElementById(listId);
    if (!datalist) {
      datalist = document.createElement("datalist");
      datalist.id = listId;
      document.body.appendChild(datalist);
    }
    textInput.setAttribute("list", listId);
    async function refreshValues() {
      const url = "/products/admin-attribute-values/?attribute=" + encodeURIComponent(attributeId) + "&q=" + encodeURIComponent(textInput.value || "");
      try {
        const response = await fetch(url, {headers: {"X-Requested-With":"XMLHttpRequest"}});
        if (!response.ok) return;
        const data = await response.json();
        datalist.replaceChildren(...(data.results || []).map(item => {
          const option = document.createElement("option");
          option.value = item.value;
          option.label = item.count ? item.value + " (" + item.count + ")" : item.value;
          return option;
        }));
      } catch (_) {}
    }
    textInput.addEventListener("focus", refreshValues, {once:true});
    textInput.addEventListener("input", refreshValues);
    await refreshValues();
  }

  document.addEventListener("change", function (event) {
    if (event.target === categoryField) loadAttributes();
    if (event.target.matches('select[name$="-attribute"]')) attachAutocomplete(event.target);
  });

  if (categoryField) {
    categoryField.addEventListener("change", loadAttributes);
    loadAttributes();
  }
  document.querySelectorAll('select[name$="-attribute"]').forEach(attachAutocomplete);
})();
