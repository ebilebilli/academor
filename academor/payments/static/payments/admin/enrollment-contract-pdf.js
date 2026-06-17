(function () {
    function getJsPDF() {
        if (window.jspdf && window.jspdf.jsPDF) {
            return window.jspdf.jsPDF;
        }
        if (window.jsPDF) {
            return window.jsPDF;
        }
        return null;
    }

    function waitForFonts() {
        if (document.fonts && document.fonts.ready) {
            return document.fonts.ready;
        }
        return Promise.resolve();
    }

    function buildExportNode(source) {
        var exportRoot = document.createElement('div');
        exportRoot.className = 'enrollment-contract-pdf-export';
        exportRoot.setAttribute('aria-hidden', 'true');
        exportRoot.innerHTML = source.innerHTML;
        document.body.appendChild(exportRoot);
        return exportRoot;
    }

    function fitCanvasToSinglePage(canvas, filename) {
        var JsPDF = getJsPDF();
        if (!JsPDF) {
            return Promise.reject(new Error('jsPDF unavailable'));
        }

        var pdf = new JsPDF({
            unit: 'mm',
            format: 'a4',
            orientation: 'portrait',
            compress: true,
        });

        var pageWidth = pdf.internal.pageSize.getWidth();
        var pageHeight = pdf.internal.pageSize.getHeight();
        var margin = 5;
        var maxWidth = pageWidth - margin * 2;
        var maxHeight = pageHeight - margin * 2;

        var renderWidth = maxWidth;
        var renderHeight = (canvas.height * renderWidth) / canvas.width;

        if (renderHeight > maxHeight) {
            renderHeight = maxHeight;
            renderWidth = (canvas.width * renderHeight) / canvas.height;
        }

        var offsetX = margin + (maxWidth - renderWidth) / 2;
        var offsetY = margin + (maxHeight - renderHeight) / 2;

        pdf.addImage(
            canvas.toDataURL('image/jpeg', 0.96),
            'JPEG',
            offsetX,
            offsetY,
            renderWidth,
            renderHeight,
            undefined,
            'FAST'
        );
        pdf.save(filename);
    }

    function exportContractPdf(source, filename) {
        var exportRoot = buildExportNode(source);

        return waitForFonts()
            .then(function () {
                return new Promise(function (resolve) {
                    requestAnimationFrame(function () {
                        requestAnimationFrame(resolve);
                    });
                });
            })
            .then(function () {
                return html2canvas(exportRoot, {
                    scale: 2,
                    useCORS: true,
                    letterRendering: true,
                    backgroundColor: '#ffffff',
                    logging: false,
                    width: exportRoot.scrollWidth,
                    height: exportRoot.scrollHeight,
                    windowWidth: exportRoot.scrollWidth,
                    windowHeight: exportRoot.scrollHeight,
                });
            })
            .then(function (canvas) {
                document.body.removeChild(exportRoot);
                return fitCanvasToSinglePage(canvas, filename);
            })
            .catch(function (err) {
                if (exportRoot.parentNode) {
                    exportRoot.parentNode.removeChild(exportRoot);
                }
                return Promise.reject(err);
            });
    }

    function boot() {
        var button = document.getElementById('enrollment-contract-pdf-download');
        var source = document.getElementById('enrollment-contract-pdf-source');
        if (!button || !source || typeof html2canvas === 'undefined') {
            return;
        }

        button.addEventListener('click', function () {
            var contractNumber =
                source.getAttribute('data-contract-number') || 'contract';
            var filename = 'tedris-muqavilesi-' + contractNumber + '.pdf';
            var defaultLabel =
                button.getAttribute('data-default-label') || button.textContent;

            button.disabled = true;
            button.textContent = button.getAttribute('data-busy-label') || '…';

            exportContractPdf(source, filename)
                .then(function () {
                    button.disabled = false;
                    button.textContent = defaultLabel;
                })
                .catch(function () {
                    button.disabled = false;
                    button.textContent = defaultLabel;
                    window.alert(
                        button.getAttribute('data-error-label') ||
                            'PDF could not be generated.'
                    );
                });
        });

        button.setAttribute('data-default-label', button.textContent);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', boot);
    } else {
        boot();
    }
})();
