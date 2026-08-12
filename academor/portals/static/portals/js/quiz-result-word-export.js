(function () {
  'use strict';

  // Word ignores base64 data-URI <img> in plain HTML documents, so results with
  // images are packaged as MHTML (multipart/related) — the format Word itself
  // writes for "Single File Web Page". Text-only results stay plain HTML.
  var BOUNDARY = '----=_NextPart_ACADEMOR_QUIZ_RESULT';
  var DOC_BASE = 'file:///C:/academor/quiz-result/';
  var CRLF = '\r\n';

  var MIME_EXTENSIONS = {
    'image/png': 'png',
    'image/jpeg': 'jpg',
    'image/jpg': 'jpg',
    'image/gif': 'gif',
    'image/bmp': 'bmp',
    'image/webp': 'webp',
    'image/svg+xml': 'svg',
  };

  function escapeHtml(value) {
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function bytesToBase64(bytes) {
    var binary = '';
    var chunk = 0x8000;
    for (var i = 0; i < bytes.length; i += chunk) {
      binary += String.fromCharCode.apply(null, bytes.subarray(i, i + chunk));
    }
    return btoa(binary);
  }

  function utf8ToBase64(text) {
    return bytesToBase64(new TextEncoder().encode(text));
  }

  function wrapBase64(value) {
    return (value.match(/.{1,76}/g) || []).join(CRLF);
  }

  function extensionForMime(mime) {
    return MIME_EXTENSIONS[String(mime || '').toLowerCase()] || 'png';
  }

  function parseDataUri(src) {
    var match = /^data:([^;,]+)(;base64)?,(.*)$/i.exec(src);
    if (!match) {
      return null;
    }
    var mime = match[1];
    var isBase64 = !!match[2];
    var data = match[3];
    return {
      mime: mime,
      base64: isBase64 ? data.replace(/\s/g, '') : btoa(unescape(data)),
    };
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

  function blobToBase64(blob) {
    if (blob.arrayBuffer) {
      return blob.arrayBuffer().then(function (buffer) {
        return bytesToBase64(new Uint8Array(buffer));
      });
    }
    return new Promise(function (resolve, reject) {
      var reader = new FileReader();
      reader.onload = function () {
        resolve(String(reader.result).split(',')[1] || '');
      };
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  }

  function fetchAsBase64(url) {
    return fetch(url, { credentials: 'same-origin' })
      .then(function (response) {
        if (!response.ok) {
          throw new Error('image fetch failed: ' + response.status);
        }
        return response.blob();
      })
      .then(function (blob) {
        return blobToBase64(blob).then(function (base64) {
          return {
            mime: blob.type || 'image/png',
            base64: base64,
          };
        });
      });
  }

  /**
   * Rewrite <img> sources to MHTML part names and collect the binary payloads.
   * Falls back to the absolute URL when an image cannot be read.
   */
  function extractHtmlWithAssets(html, assets) {
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
        if (!rawSrc) {
          return Promise.resolve();
        }
        var inline = parseDataUri(rawSrc);
        var loader = inline ? Promise.resolve(inline) : fetchAsBase64(resolveUrl(rawSrc));
        return loader
          .then(function (asset) {
            var name = 'image' + String(assets.length + 1).padStart(3, '0') + '.' +
              extensionForMime(asset.mime);
            assets.push({
              name: name,
              mime: asset.mime || 'image/png',
              base64: asset.base64,
            });
            img.setAttribute('src', name);
            img.removeAttribute('srcset');
          })
          .catch(function () {
            img.setAttribute('src', resolveUrl(rawSrc));
          });
      }),
    ).then(function () {
      return container.innerHTML;
    });
  }

  function renderContent(field, assets) {
    if (field == null || field === '') {
      return Promise.resolve('');
    }
    var raw = typeof field === 'string' ? field : field.value || field.text || '';
    if (!raw) {
      return Promise.resolve('');
    }
    var isHtml = typeof field === 'object' && field.is_html;
    if (isHtml || /<[a-z][\s\S]*>/i.test(raw)) {
      return extractHtmlWithAssets(raw, assets);
    }
    return Promise.resolve(escapeHtml(raw));
  }

  function buildBody(data, assets) {
    var head = [];
    head.push('<h1>' + escapeHtml(data.title || 'Quiz result') + '</h1>');
    head.push(
      '<p><strong>' +
        escapeHtml(data.student_label || 'Student') +
        ':</strong> ' +
        escapeHtml(data.student_name || '—') +
        '</p>',
    );
    head.push(
      '<p><strong>' +
        escapeHtml(data.quiz_label || 'Quiz') +
        ':</strong> ' +
        escapeHtml(data.quiz_topic || '—') +
        '</p>',
    );
    head.push(
      '<p><strong>' +
        escapeHtml(data.score_label || 'Score') +
        ':</strong> ' +
        escapeHtml(data.score_text || '—') +
        '</p>',
    );
    if (data.completed_at) {
      head.push(
        '<p><strong>' +
          escapeHtml(data.date_label || 'Submitted') +
          ':</strong> ' +
          escapeHtml(data.completed_at) +
          '</p>',
      );
    }
    head.push('<hr>');

    // Sequential so image part numbering follows question order.
    var blocks = [];
    var chain = Promise.resolve();
    (data.items || []).forEach(function (item) {
      chain = chain
        .then(function () {
          return renderContent(item.question, assets);
        })
        .then(function (questionHtml) {
          return renderContent(item.student_answer, assets).then(function (studentHtml) {
            return renderContent(item.correct_answer, assets).then(function (correctHtml) {
              var block = [];
              block.push(
                '<div style="margin:14pt 0;padding-bottom:10pt;border-bottom:1px solid #cccccc;">',
              );
              block.push(
                '<p style="margin:0 0 6pt;"><strong>' +
                  escapeHtml(data.question_label || 'Question') +
                  ' ' +
                  escapeHtml(item.number) +
                  '</strong>' +
                  (item.status ? ' — ' + escapeHtml(item.status) : '') +
                  '</p>',
              );
              if (questionHtml) {
                block.push('<div style="margin:0 0 8pt;">' + questionHtml + '</div>');
              }
              block.push(
                '<p style="margin:0 0 4pt;"><strong>' +
                  escapeHtml(data.your_answer_label || 'Your answer') +
                  ':</strong></p>',
              );
              block.push('<div style="margin:0 0 8pt;">' + (studentHtml || '—') + '</div>');
              if (correctHtml) {
                block.push(
                  '<p style="margin:0 0 4pt;"><strong>' +
                    escapeHtml(data.correct_answer_label || 'Correct answer') +
                    ':</strong></p>',
                );
                block.push('<div style="margin:0;">' + correctHtml + '</div>');
              }
              block.push('</div>');
              blocks.push(block.join(''));
            });
          });
        });
    });

    return chain.then(function () {
      var tail = [];
      if (data.teacher_feedback) {
        tail.push('<h2>' + escapeHtml(data.feedback_label || 'Teacher feedback') + '</h2>');
        tail.push('<p>' + escapeHtml(data.teacher_feedback).replace(/\n/g, '<br>') + '</p>');
      }
      return head.join('') + blocks.join('') + tail.join('');
    });
  }

  function buildHtmlDocument(data, body) {
    return (
      '<!DOCTYPE html>' +
      '<html xmlns:o="urn:schemas-microsoft-com:office:office" ' +
      'xmlns:w="urn:schemas-microsoft-com:office:word" xmlns="http://www.w3.org/TR/REC-html40">' +
      '<head>' +
      '<meta http-equiv="Content-Type" content="text/html; charset=utf-8">' +
      '<title>' +
      escapeHtml(data.title || 'Quiz result') +
      '</title>' +
      '<!--[if gte mso 9]><xml><w:WordDocument><w:View>Print</w:View>' +
      '<w:Zoom>100</w:Zoom></w:WordDocument></xml><![endif]-->' +
      '<style>body{font-family:"Segoe UI",Calibri,Arial,sans-serif;font-size:12pt;line-height:1.45}' +
      'h1{font-size:18pt}h2{font-size:14pt}' +
      'img{max-width:460px;height:auto;vertical-align:middle}' +
      'table{border-collapse:collapse}td,th{border:1px solid #999999;padding:4pt}' +
      'sub,sup{font-size:0.75em}</style>' +
      '</head><body lang="EN">' +
      body +
      '</body></html>'
    );
  }

  function buildMhtml(data, html, assets) {
    var parts = [];
    parts.push('MIME-Version: 1.0');
    parts.push('Content-Type: multipart/related; type="text/html"; boundary="' + BOUNDARY + '"');
    parts.push('X-Document-Type: Word.Document');
    parts.push('');
    parts.push('--' + BOUNDARY);
    parts.push('Content-Type: text/html; charset="utf-8"');
    parts.push('Content-Transfer-Encoding: base64');
    parts.push('Content-Location: ' + DOC_BASE + 'result.htm');
    parts.push('');
    parts.push(wrapBase64(utf8ToBase64(html)));

    assets.forEach(function (asset) {
      parts.push('');
      parts.push('--' + BOUNDARY);
      parts.push('Content-Type: ' + asset.mime);
      parts.push('Content-Transfer-Encoding: base64');
      parts.push('Content-Location: ' + DOC_BASE + asset.name);
      parts.push('');
      parts.push(wrapBase64(asset.base64));
    });

    parts.push('');
    parts.push('--' + BOUNDARY + '--');
    parts.push('');
    return parts.join(CRLF);
  }

  function triggerDownload(filename, content, mimeType) {
    var blob = new Blob([content], { type: mimeType });
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
    var assets = [];
    var originalLabel = button ? button.innerHTML : '';
    if (button) {
      button.disabled = true;
    }
    return buildBody(data, assets)
      .then(function (body) {
        var html = buildHtmlDocument(data, body);
        var filename = data.filename || 'quiz-result.doc';
        if (assets.length) {
          triggerDownload(filename, buildMhtml(data, html, assets), 'application/msword');
        } else {
          triggerDownload(filename, '\ufeff' + html, 'application/msword;charset=utf-8');
        }
      })
      .finally(function () {
        if (button) {
          button.disabled = false;
          button.innerHTML = originalLabel;
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
