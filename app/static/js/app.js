document.addEventListener('DOMContentLoaded', () => {
  setTimeout(() => {
    document.querySelectorAll('.alert').forEach(el => {
      if (el.classList.contains('show')) {
        new bootstrap.Alert(el).close();
      }
    });
  }, 5000);
});