
    $('#mb').on('shown.bs.modal', function v () {
  // Ton code JS ici
  document.addEventListener("DOMContentLoaded", () => {
  // Cherche tous les formulaires SFE sur la page
  const forms = document.querySelectorAll('form[data-form-type="client-sfe"]');

  forms.forEach(form => {
    const typeSelect = form.querySelector("#typeClient");
    const zones = form.querySelectorAll(".zone-type");

    if (!typeSelect) return;

    typeSelect.addEventListener("change", e => {
      const type = e.target.value;

      // Cache toutes les zones
      zones.forEach(z => z.classList.add("d-none"));

      // Affiche la bonne zone selon le type
      if (type === "physique") form.querySelector("#zonePhysique")?.classList.remove("d-none");
      if (type === "morale") form.querySelector("#zoneMorale")?.classList.remove("d-none");
      if (type === "etranger") form.querySelector("#zoneEtranger")?.classList.remove("d-none");
    });
  });
});
  document.getElementById("typeClient").addEventListener("change", function() {
      const type = this.value;
      document.getElementById("fieldsPhysique").classList.add("d-none");
      document.getElementById("fieldsMorale").classList.add("d-none");
      document.getElementById("fieldsEtranger").classList.add("d-none");
      if (type === "physique") document.getElementById("fieldsPhysique").classList.remove("d-none");
      if (type === "morale") document.getElementById("fieldsMorale").classList.remove("d-none");
      if (type === "etranger") document.getElementById("fieldsEtranger").classList.remove("d-none");
    });

  // Exemple :
  document.querySelector('#monChamp').addEventListener('change', function() {
    console.log('Champ modifié');
  });
});
