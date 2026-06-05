// 医联通 SmartMed v2 — 前端交互
document.addEventListener('DOMContentLoaded', function() {
  // Auto-dismiss flash
  document.querySelectorAll('.flash').forEach(function(el) {
    setTimeout(function() {
      el.style.opacity = '0';
      el.style.transform = 'translateX(10px)';
      el.style.transition = 'all .3s ease';
      setTimeout(function() { el.remove(); }, 300);
    }, 3500);
  });

  // Modal: click outside close
  document.querySelectorAll('.modal').forEach(function(m) {
    m.addEventListener('click', function(e) {
      if (e.target === m) m.classList.remove('active');
    });
  });

  // ESC close modal
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      document.querySelectorAll('.modal.active').forEach(function(m) {
        m.classList.remove('active');
      });
    }
  });

  // Notification toggle
  var notifyBtn = document.getElementById('notifyBtn');
  var notifyDropdown = document.getElementById('notifyDropdown');
  if (notifyBtn && notifyDropdown) {
    notifyBtn.addEventListener('click', function(e) {
      e.stopPropagation();
      notifyDropdown.classList.toggle('show');
    });
    document.addEventListener('click', function() {
      notifyDropdown.classList.remove('show');
    });
  }

  // Symptom checker
  var symptomTags = document.querySelectorAll('.symptom-tag');
  if (symptomTags.length > 0) {
    symptomTags.forEach(function(tag) {
      tag.addEventListener('click', function() {
        this.classList.toggle('selected');
        checkSymptoms();
      });
    });
  }

  // Rating stars
  var ratingStars = document.querySelectorAll('.rating-stars span');
  if (ratingStars.length > 0) {
    var ratingInput = document.getElementById('ratingValue');
    ratingStars.forEach(function(star) {
      star.addEventListener('click', function() {
        var val = parseInt(this.dataset.value);
        if (ratingInput) ratingInput.value = val;
        ratingStars.forEach(function(s, i) {
          s.classList.toggle('active', i < val);
        });
      });
      star.addEventListener('mouseenter', function() {
        var val = parseInt(this.dataset.value);
        ratingStars.forEach(function(s, i) {
          s.classList.toggle('active', i < val);
        });
      });
    });
    var ratingContainer = document.querySelector('.rating-stars');
    if (ratingContainer) {
      ratingContainer.addEventListener('mouseleave', function() {
        var val = ratingInput ? parseInt(ratingInput.value) : 0;
        ratingStars.forEach(function(s, i) {
          s.classList.toggle('active', i < val);
        });
      });
    }
  }

  // Chat: quick reply click
  document.querySelectorAll('.quick-reply').forEach(function(btn) {
    btn.addEventListener('click', function() {
      var input = document.getElementById('chatInput');
      if (input) {
        input.value = this.textContent.trim();
        input.focus();
      }
    });
  });

  // Scroll chat to bottom
  var chatMessages = document.getElementById('chatMessages');
  if (chatMessages) {
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  // Enter to send
  var chatInput = document.getElementById('chatInput');
  if (chatInput) {
    chatInput.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        var form = document.getElementById('chatForm');
        if (form) form.dispatchEvent(new Event('submit'));
      }
    });
  }

  // Article category filter
  var articleCatBtns = document.querySelectorAll('.article-filter');
  articleCatBtns.forEach(function(btn) {
    btn.addEventListener('click', function() {
      articleCatBtns.forEach(function(b) { b.classList.remove('active'); });
      this.classList.add('active');
      var cat = this.dataset.cat;
      document.querySelectorAll('.article-card').forEach(function(card) {
        if (cat === 'all' || card.dataset.cat === cat) {
          card.style.display = '';
        } else {
          card.style.display = 'none';
        }
      });
    });
  });
});

// Symptom-to-dept mapping
var symptomMap = {
  '头痛': '神经内科', '头晕': '神经内科', '失眠': '神经内科',
  '咳嗽': '内科', '发热': '内科', '喉咙痛': '内科', '流鼻涕': '内科',
  '胸痛': '心血管内科', '心悸': '心血管内科', '胸闷': '心血管内科',
  '腹痛': '消化内科', '腹泻': '消化内科', '恶心': '消化内科', '便秘': '消化内科',
  '腰痛': '骨科', '关节痛': '骨科', '骨折': '骨科',
  '皮疹': '皮肤科', '瘙痒': '皮肤科', '痘痘': '皮肤科',
  '视力模糊': '眼科', '眼干': '眼科', '眼红': '眼科',
  '牙痛': '口腔科', '口腔溃疡': '口腔科',
  '焦虑': '心理科', '抑郁': '心理科', '压力大': '心理科',
  '月经不调': '妇产科', '痛经': '妇产科',
  '小儿发热': '儿科', '小儿咳嗽': '儿科',
};

function checkSymptoms() {
  var resultDiv = document.getElementById('symptomResult');
  if (!resultDiv) return;
  var selected = [];
  document.querySelectorAll('.symptom-tag.selected').forEach(function(t) {
    selected.push(t.textContent.trim());
  });
  if (selected.length === 0) {
    resultDiv.style.display = 'none';
    return;
  }
  var deptScores = {};
  selected.forEach(function(s) {
    var dept = symptomMap[s];
    if (dept) deptScores[dept] = (deptScores[dept] || 0) + 1;
  });
  var topDept = Object.entries(deptScores).sort(function(a, b) { return b[1] - a[1]; })[0];
  if (topDept) {
    resultDiv.style.display = 'block';
    resultDiv.innerHTML = '<div class="symptom-result"><p style="color:var(--text-muted)">根据您的症状，建议就诊科室</p><div class="rec-dept">' + topDept[0] + '</div><p style="color:var(--text-muted);font-size:.85rem">匹配症状: ' + selected.join('、') + '</p><a href="/patient/doctors" class="btn btn-primary mt-4">查看' + topDept[0] + '医生 →</a></div>';
  }
}

function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('collapsed');
}

function showBookModal(id, name) {
  var el = document.getElementById('bookDoctorId');
  if (el) el.value = id;
  var nameEl = document.getElementById('bookDoctorName');
  if (nameEl) nameEl.textContent = name;
  var modal = document.getElementById('bookModal');
  if (modal) modal.classList.add('active');
}

function closeBookModal() {
  var modal = document.getElementById('bookModal');
  if (modal) modal.classList.remove('active');
}
