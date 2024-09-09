  document.getElementById('register-form').addEventListener('submit', function(event) {
    var termsCheckbox = document.getElementById('terms-checkbox');
    if (termsCheckbox.checked) {
      document.cookie = "termsAccepted=true; path=/; max-age=31536000"; // Cookie válido por 1 ano
    } else {
      event.preventDefault(); // Previne o envio do formulário se o checkbox não estiver marcado
      alert('Você precisa aceitar os Termos e Condições e a Política de Privacidade.');
    }
  });
