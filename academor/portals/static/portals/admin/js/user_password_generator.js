(function () {
  function generatePassword(length) {
    var chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789!@#$%&*';
    var password = '';
    var array = new Uint32Array(length);
    if (window.crypto && window.crypto.getRandomValues) {
      window.crypto.getRandomValues(array);
      for (var i = 0; i < length; i += 1) {
        password += chars[array[i] % chars.length];
      }
      return password;
    }
    for (var j = 0; j < length; j += 1) {
      password += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return password;
  }

  function initPasswordGenerator() {
    var password1 = document.getElementById('id_password1');
    var password2 = document.getElementById('id_password2');
    if (!password1 || !password2 || password1.type === 'password') {
      return;
    }

    var row = password1.closest('.form-row') || password1.closest('.field-password1');
    if (!row || row.querySelector('.portal-generate-password')) {
      return;
    }

    var button = document.createElement('button');
    button.type = 'button';
    button.className = 'button portal-generate-password';
    button.textContent = password1.dataset.generateLabel || 'Generate random password';

    var hint = document.createElement('p');
    hint.className = 'help portal-generated-password-note';
    hint.hidden = true;
    var generatedPrefix = password1.dataset.generatedLabel || 'Generated password';

    button.addEventListener('click', function () {
      var value = generatePassword(14);
      password1.value = value;
      password2.value = value;
      password1.focus();
      password1.select();
      hint.textContent = generatedPrefix + ': ' + value;
      hint.hidden = false;
    });

    row.appendChild(button);
    row.appendChild(hint);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPasswordGenerator);
  } else {
    initPasswordGenerator();
  }
})();
