document.addEventListener('DOMContentLoaded', () => {
  const debounce = (fn, delay=400) => {
    let t; return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), delay); };
  };
  const ensureMsg = (input) => {
    let el = input.parentElement.querySelector('.field-hint');
    if (!el) {
      el = document.createElement('div');
      el.className = 'field-hint text-xs mt-1';
      input.parentElement.appendChild(el);
    }
    return el;
  };
  const setHint = (el, ok, msg) => {
    el.textContent = msg || '';
    el.classList.toggle('text-green-600', !!ok);
    el.classList.toggle('text-red-600', !ok);
  };

  // Signup form enhancements
  const signupForm = document.querySelector('form#signup_form');
  if (signupForm) {
    const username = signupForm.querySelector('input[name="username"]');
    const email = signupForm.querySelector('input[name="email"]');
    const pw1 = signupForm.querySelector('input[name="password1"]');
    const pw2 = signupForm.querySelector('input[name="password2"]');

    if (username) {
      username.setAttribute('minlength', '3');
      const onUser = debounce(async () => {
        const v = username.value.trim();
        const hint = ensureMsg(username);
        if (v.length < 3) { setHint(hint, false, 'At least 3 characters'); return; }
        try {
          const r = await fetch(`/accounts/check-username/?u=${encodeURIComponent(v)}`, { headers: { 'Accept': 'application/json' } });
          const j = await r.json();
          setHint(hint, j.available, j.message);
        } catch { setHint(hint, false, 'Check failed'); }
      });
      username.addEventListener('input', onUser);
    }

    if (email) {
      email.setAttribute('type', 'email');
      const onEmail = debounce(async () => {
        const v = email.value.trim();
        const hint = ensureMsg(email);
        if (!v) { setHint(hint, false, 'Email required'); return; }
        try {
          const r = await fetch(`/accounts/check-email/?e=${encodeURIComponent(v)}`, { headers: { 'Accept': 'application/json' } });
          const j = await r.json();
          setHint(hint, j.available, j.message);
        } catch { setHint(hint, false, 'Check failed'); }
      });
      email.addEventListener('input', onEmail);
    }

    const strength = (s) => {
      let score = 0; if (s.length >= 8) score++; if (/[A-Z]/.test(s)) score++; if (/[a-z]/.test(s)) score++; if (/[0-9]/.test(s)) score++; if (/[^A-Za-z0-9]/.test(s)) score++;
      return score;
    };

    if (pw1) {
      const onPw = () => {
        const hint = ensureMsg(pw1);
        const sc = strength(pw1.value);
        const labels = ['Very weak','Weak','Okay','Good','Strong'];
        setHint(hint, sc >= 3, `Strength: ${labels[Math.max(0, sc-1)]}`);
      };
      pw1.addEventListener('input', onPw);
    }
    if (pw1 && pw2) {
      const onMatch = () => {
        const hint = ensureMsg(pw2);
        const ok = pw2.value && pw1.value === pw2.value;
        setHint(hint, ok, ok ? 'Passwords match' : 'Passwords do not match');
      };
      pw1.addEventListener('input', onMatch);
      pw2.addEventListener('input', onMatch);
    }
  }

  // Event form constraints
  const eventForm = document.querySelector('form[action*="/events/"][method="post"]');
  if (eventForm) {
    const dateInput = eventForm.querySelector('input[type="date"]');
    if (dateInput) {
      const today = new Date(); today.setHours(0,0,0,0);
      const iso = today.toISOString().slice(0,10);
      dateInput.setAttribute('min', iso);
      dateInput.addEventListener('input', () => {
        const v = new Date(dateInput.value);
        v.setHours(0,0,0,0);
        if (dateInput.value && v < today) {
          dateInput.setCustomValidity('Date must be today or later');
        } else { dateInput.setCustomValidity(''); }
      });
    }
  }

  // Category form simple minlength helper
  const categoryForm = document.querySelector('form[action*="/categories/"][method="post"]');
  if (categoryForm) {
    const name = categoryForm.querySelector('input[name="name"]');
    if (name) {
      name.setAttribute('minlength', '2');
      name.addEventListener('input', () => {
        const hint = ensureMsg(name);
        const ok = name.value.trim().length >= 2;
        setHint(hint, ok, ok ? '' : 'At least 2 characters');
      });
    }
  }

  // Debounced search submit for event list
  const searchForm = document.querySelector('form[action$="/events/"][method="GET"]');
  if (searchForm) {
    const q = searchForm.querySelector('input[name="q"]');
    if (q) {
      q.addEventListener('input', debounce(() => searchForm.requestSubmit(), 500));
    }
  }
});