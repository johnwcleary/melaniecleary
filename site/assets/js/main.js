// Lightbox for photo galleries: click a thumbnail to view it large, arrows/swipe to move between photos.
(function () {
  const links = Array.from(document.querySelectorAll("[data-lightbox]"));
  if (!links.length || typeof HTMLDialogElement !== "function") return;

  const dialog = document.createElement("dialog");
  dialog.className = "lightbox";
  dialog.innerHTML =
    '<img alt="">' +
    '<button class="lb-close" type="button" aria-label="Close">×</button>' +
    '<button class="lb-prev" type="button" aria-label="Previous photo">‹</button>' +
    '<button class="lb-next" type="button" aria-label="Next photo">›</button>' +
    '<p class="lb-count"></p>';
  document.body.appendChild(dialog);

  const img = dialog.querySelector("img");
  const count = dialog.querySelector(".lb-count");
  let index = 0;

  function show(i) {
    index = (i + links.length) % links.length;
    const link = links[index];
    img.src = link.href;
    img.alt = link.querySelector("img").alt;
    count.textContent = index + 1 + " / " + links.length;
  }

  links.forEach((link, i) =>
    link.addEventListener("click", (e) => {
      e.preventDefault();
      show(i);
      dialog.showModal();
    })
  );

  dialog.querySelector(".lb-close").addEventListener("click", () => dialog.close());
  dialog.querySelector(".lb-prev").addEventListener("click", () => show(index - 1));
  dialog.querySelector(".lb-next").addEventListener("click", () => show(index + 1));
  dialog.addEventListener("click", (e) => {
    if (e.target === dialog) dialog.close();
  });
  dialog.addEventListener("keydown", (e) => {
    if (e.key === "ArrowLeft") show(index - 1);
    if (e.key === "ArrowRight") show(index + 1);
  });

  let startX = null;
  dialog.addEventListener("touchstart", (e) => (startX = e.touches[0].clientX), { passive: true });
  dialog.addEventListener("touchend", (e) => {
    if (startX === null) return;
    const dx = e.changedTouches[0].clientX - startX;
    if (Math.abs(dx) > 40) show(index + (dx < 0 ? 1 : -1));
    startX = null;
  });
})();
