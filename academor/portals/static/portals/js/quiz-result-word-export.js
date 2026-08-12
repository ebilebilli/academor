(function () {
  'use strict';

  function escapeHtml(value) {
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function blobToDataUrl(blob) {
    return new Promise(function (resolve, reject) {
      var reader = new FileReader();
      reader.onload = function () {
        resolve(reader.result);
      };
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  }

  function resolveUrl(src) {
    if (!src) {
      return '';
    }
    if (/^(data:|https?:|blob:)/i.test(src)) {
      return src;
    }
    if (src.indexOf('//') === 0) {
      return window.location.protocol + src;
    }
    try {
      return new URL(src, window.location.href).href;
    } catch (err) {
      return src;
    }
  }

  function inlineImagesInHtml(html) {
    if (!html) {
      return Promise.resolve('');
    }
    var container = document.createElement('div');
    container.innerHTML = html;
    var images = Array.prototype.slice.call(container.querySelectorAll('img'));
    if (!images.length) {
      return Promise.resolve(container.innerHTML);
    }

    return Promise.all(
      images.map(function (img) {
        var rawSrc = img.getAttribute('src') || '';
        if (!rawSrc || /^data:/i.test(rawSrc)) {
          return Promise.resolve();
        }
        var absolute = resolveUrl(rawSrc);
        img.setAttribute('src', absolute);
        return fetch(absolute, { credentials: 'same-origin', mode: 'cors' })
          .then(function (response) {
            if (!response.ok) {
              throw new Error('image fetch failed');
            }
            return response.blob();
          })
          .then(blobToDataUrl)
          .then(function (dataUrl) {
            img.setAttribute('src', dataUrl);
          })
          .catch(function () {
            img.setAttribute('src', absolute);
          });
      }),
    ).then(function () {
      return container.innerHTML;
    });
  }

  function renderContent(field) {
    if (field == null || field === '') {
      return Promise.resolve('—');
    }
    // Backward-compatible: plain string
    if (typeof field === 'string') {
      if (/<[a-z][\s\S]*>/i.test(field)) {
        return inlineImagesInHtml(field);
      }
      return Promise.resolve(escapeHtml(field) || '—');
    }
    if (field.is_html && field.value) {
      return inlineImagesInHtml(field.value);
    }
    if (field.value) {
      if (field.is_html || /<[a-z][\s\S]*>/i.test(field.value)) {
        return inlineImagesInHtml(field.value);
      }
      return Promise.resolve(escapeHtml(field.value) || '—');
    }
    if (field.text) {
      return Promise.resolve(escapeHtml(field.text) || '—');
    }
    return Promise.resolve('—');
  }

  function buildBody(data) {
    var parts = [];
    parts.push('<h1>' + escapeHtml(data.title || 'Quiz result') + '</h1>');
    parts.push(
      '<p><strong>' +
        escapeHtml(data.student_label || 'Student') +
        ':</strong> ' +
        escapeHtml(data.student_name || '—') +
        '</p>',
    );
    parts.push(
      '<p><strong>' +
        escapeHtml(data.quiz_label || 'Quiz') +
        ':</strong> ' +
        escapeHtml(data.quiz_topic || '—') +
        '</p>',
    );
    parts.push(
      '<p><strong>' +
        escapeHtml(data.score_label || 'Score') +
        ':</strong> ' +
        escapeHtml(data.score_text || '—') +
        '</p>',
    );
    if (data.completed_at) {
      parts.push(
        '<p><strong>' +
          escapeHtml(data.date_label || 'Submitted') +
          ':</strong> ' +
          escapeHtml(data.completed_at) +
          '</p>',
      );
    }
    parts.push('<hr>');

    var itemJobs = (data.items || []).map(function (item) {
      return Promise.all([
        renderContent(item.question),
        renderContent(item.student_answer),
        renderContent(item.correct_answer),
      ]).then(function (rendered) {
        var questionHtml = rendered[0];
        var studentHtml = rendered[1];
        var correctHtml = rendered[2];
        var block = [];
        block.push('<div style="margin:14pt 0;padding-bottom:10pt;border-bottom:1px solid #ccc;">');
        block.push(
          '<p style="margin:0 0 6pt;"><strong>' +
            escapeHtml(data.question_label || 'Question') +
            ' ' +
            escapeHtml(item.number) +
            '</strong>' +
            (item.status ? ' — ' + escapeHtml(item.status) : '') +
            '</p>',
        );
        if (questionHtml && questionHtml !== '—') {
          block.push('<div style="margin:0 0 6pt;">' + questionHtml + '</div>');
        }
        block.push(
          '<p style="margin:0 0 4pt;"><strong>' +
            escapeHtml(data.your_answer_label || 'Your answer') +
            ':</strong></p>',
        );
        block.push('<div style="margin:0 0 6pt;">' + studentHtml + '</div>');
        if (item.correct_answer && (item.correct_answer.value || item.correct_answer.text || typeof item.correct_answer === 'string')) {
          var hasCorrect =
            typeof item.correct_answer === 'string'
              ? !!item.correct_answer
              : !!(item.correct_answer.value || item.correct_answer.text);
          if (hasCorrect && correctHtml && correctHtml !== '—') {
            block.push(
              '<p style="margin:0 0 4pt;"><strong>' +
                escapeHtml(data.correct_answer_label || 'Correct answer') +
                ':</strong></p>',
            );
            block.push('<div style="margin:0;">' + correctHtml + '</div>');
          }
        }
        block.push('</div>');
        return block.join('');
      });
    });

    return Promise.all(itemJobs).then(function (blocks) {
      parts.push.apply(parts, blocks);
      if (data.teacher_feedback) {
        parts.push('<h2>' + escapeHtml(data.feedback_label || 'Teacher feedback') + '</h2>');
        parts.push('<p>' + escapeHtml(data.teacher_feedback).replace(/\n/g, '<br>') + '</p>');
      }
      return parts.join('');
    });
  }

  function triggerDownload(filename, html) {
    var blob = new Blob(['\ufeff', html], { type: 'application/msword;charset=utf-8' });
    var url = URL.createObjectURL(blob);
    var link = document.createElement('a');
    link.href = url;
    link.download = filename || 'quiz-result.doc';
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(function () {
      URL.revokeObjectURL(url);
    }, 1000);
  }

  function downloadWord(data, button) {
    if (button) {
      button.disabled = true;
    }
    return buildBody(data)
      .then(function (body) {
        var html =
          '<!DOCTYPE html><html xmlns:o="urn:schemas-microsoft-com:office:office" ' +
          'xmlns:w="urn:schemas-microsoft-com:office:word" xmlns="http://www.w3.org/TR/REC-html40">' +
          '<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8">' +
          '<meta charset="utf-8"><title>' +
          escapeHtml(data.title || 'Quiz result') +
          '</title>' +
          '<!--[if gte mso 9]><xml><w:WordDocument><w:View>Print</w:View></w:WordDocument></xml><![endif]-->' +
          '<style>body{font-family:"Segoe UI",Calibri,Arial,sans-serif;font-size:12pt;line-height:1.45}' +
          'h1{font-size:18pt}h2{font-size:14pt}' +
          'img{max-width:480px;height:auto;vertical-align:middle}' +
          'sub,sup{font-size:0.75em}</style></head><body>' +
          body +
          '</body></html>';
        triggerDownload(data.filename || 'quiz-result.doc', html);
      })
      .finally(function () {
        if (button) {
          button.disabled = false;
        }
      });
  }

  function readPayload(button) {
    var targetId = button.getAttribute('data-quiz-result-word-source');
    if (targetId) {
      var node = document.getElementById(targetId);
      if (node && node.textContent) {
        return JSON.parse(node.textContent);
      }
    }
    var raw = button.getAttribute('data-quiz-result-word');
    if (raw) {
      return JSON.parse(raw);
    }
    return null;
  }

  function onClick(event) {
    var button = event.target.closest('[data-quiz-result-word-export]');
    if (!button) {
      return;
    }
    event.preventDefault();
    try {
      var data = readPayload(button);
      if (!data) {
        return;
      }
      downloadWord(data, button).catch(function (err) {
        console.error('Quiz result Word export failed', err);
      });
    } catch (err) {
      console.error('Quiz result Word export failed', err);
    }
  }

  document.addEventListener('click', onClick);
})();
