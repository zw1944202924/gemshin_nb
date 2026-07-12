const body = document.body;
const menuToggle = document.querySelector("[data-menu-toggle]");
const mobileBackdrop = document.querySelector("[data-mobile-backdrop]");

if (menuToggle) {
  menuToggle.addEventListener("click", () => {
    body.classList.toggle("menu-open");
  });
}

if (mobileBackdrop) {
  mobileBackdrop.addEventListener("click", () => {
    body.classList.remove("menu-open");
  });
}

document.querySelectorAll("[data-demo-group]").forEach((group) => {
  const buttons = group.querySelectorAll("[data-demo-toggle]");
  const panels = group.querySelectorAll("[data-demo-panel]");
  const activate = (name) => {
    buttons.forEach((button) => {
      button.classList.toggle("is-active", button.dataset.demoToggle === name);
      button.setAttribute("aria-pressed", String(button.dataset.demoToggle === name));
    });
    panels.forEach((panel) => {
      panel.hidden = panel.dataset.demoPanel !== name;
    });
  };

  buttons.forEach((button) => {
    button.addEventListener("click", () => activate(button.dataset.demoToggle));
  });

  const active = [...buttons].find((button) => button.classList.contains("is-active"));
  activate(active ? active.dataset.demoToggle : buttons[0]?.dataset.demoToggle);
});
