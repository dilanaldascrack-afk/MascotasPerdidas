// Navbar scroll
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  navbar?.classList.toggle('scrolled', window.scrollY > 20);
});

// Mobile nav toggle
document.getElementById('navToggle')?.addEventListener('click', () => {
  document.getElementById('navLinks')?.classList.toggle('open');
});

// Auto-dismiss flash messages
setTimeout(() => {
  document.querySelectorAll('.flash').forEach(el => el.remove());
}, 5000);

// Footer stats
fetch('/api/stats').then(r => r.json()).then(d => {
  const el = id => document.getElementById(id);
  if(el('footerLost')) el('footerLost').textContent = d.total_lost;
  if(el('footerFound')) el('footerFound').textContent = d.total_found;
  if(el('footerResolved')) el('footerResolved').textContent = d.total_resolved;
}).catch(() => {});

// Photo preview
const photoInput = document.getElementById('photoInput');
if (photoInput) {
  const area = document.getElementById('photoUploadArea');
  const placeholder = document.getElementById('photoPlaceholder');
  const previewWrap = document.getElementById('photoPreviewWrap');
  const preview = document.getElementById('photoPreview');

  photoInput.addEventListener('change', function() {
    if (this.files && this.files[0]) {
      const reader = new FileReader();
      reader.onload = e => {
        preview.src = e.target.result;
        placeholder.classList.add('hidden');
        previewWrap.classList.remove('hidden');
      };
      reader.readAsDataURL(this.files[0]);
    }
  });

  area.addEventListener('dragover', e => { e.preventDefault(); area.classList.add('drag-over'); });
  area.addEventListener('dragleave', () => area.classList.remove('drag-over'));
  area.addEventListener('drop', e => {
    e.preventDefault();
    area.classList.remove('drag-over');
    if (e.dataTransfer.files[0]) {
      photoInput.files = e.dataTransfer.files;
      photoInput.dispatchEvent(new Event('change'));
    }
  });
}

function removePhoto() {
  document.getElementById('photoInput').value = '';
  document.getElementById('photoPlaceholder').classList.remove('hidden');
  document.getElementById('photoPreviewWrap').classList.add('hidden');
}

// Status toggle UI
function updateStatusUI(radio) {
  document.querySelectorAll('.status-toggle').forEach(el => el.classList.remove('active'));
  radio.closest('.status-toggle').classList.add('active');
}

// Filter radio toggle UI
document.querySelectorAll('.filter-toggle input[type=radio]').forEach(radio => {
  radio.addEventListener('change', () => {
    document.querySelectorAll('.filter-toggle').forEach(el => el.classList.remove('active'));
    radio.closest('.filter-toggle').classList.add('active');
  });
});

// Mobile filters sidebar
document.getElementById('btnToggleFilters')?.addEventListener('click', () => {
  document.getElementById('filtersSidebar')?.classList.toggle('open');
});

// Submit loading state
document.getElementById('reportForm')?.addEventListener('submit', function() {
  const btn = document.getElementById('btnSubmitReport');
  if (btn) {
    btn.querySelector('.btn-submit-text')?.classList.add('hidden');
    btn.querySelector('.btn-submit-loading')?.classList.remove('hidden');
    btn.disabled = true;
  }
});
