/**
 * Admin Panel Image Compress - Browser-də WebP-yə çevirir
 * Server RAM istifadə etmir - bütün iş browser-də olur
 */
(function() {
    'use strict';
    
    // jQuery-ni tap
    function getJQuery() {
        if (typeof django !== 'undefined' && django.jQuery) {
            return django.jQuery;
        }
        if (typeof jQuery !== 'undefined') {
            return jQuery;
        }
        if (typeof window.$ !== 'undefined' && typeof window.$.fn !== 'undefined' && typeof window.$.fn.jquery !== 'undefined') {
            return window.$;
        }
        return null;
    }
    
    // Script-i işə sal
    function startScript() {
        var $ = getJQuery();
        
        // Əgər jQuery yoxdursa, gözlə
        if (!$) {
            setTimeout(startScript, 100);
            return;
        }
        
        // jQuery-ni local scope-da saxla
        (function($) {
            console.log('[Image Compress] jQuery loaded, version:', $.fn.jquery);
            
            // WebP dəstəkləyirmi yoxla
            function supportsWebP() {
                try {
                    var canvas = document.createElement('canvas');
                    canvas.width = 1;
                    canvas.height = 1;
                    return canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0;
                } catch (e) {
                    return false;
                }
            }

            if (!supportsWebP()) {
                console.warn('[Image Compress] Browser does not support WebP');
                return;
            }

            // Şəkil compress funksiyası
            function compressImageToWebP(file, maxWidth, maxHeight, quality) {
                return new Promise(function(resolve, reject) {
                    var reader = new FileReader();
                    
                    reader.onload = function(e) {
                        var img = new Image();
                        
                        img.onload = function() {
                            var canvas = document.createElement('canvas');
                            var width = img.width;
                            var height = img.height;
                            
                            // Ölçüləri hesabla (aspect ratio saxla)
                            if (width > maxWidth || height > maxHeight) {
                                var ratio = Math.min(maxWidth / width, maxHeight / height);
                                width = width * ratio;
                                height = height * ratio;
                            }
                            
                            canvas.width = width;
                            canvas.height = height;
                            
                            var ctx = canvas.getContext('2d');
                            ctx.drawImage(img, 0, 0, width, height);
                            
                            // WebP-yə çevir
                            canvas.toBlob(function(blob) {
                                if (blob) {
                                    var nameWithoutExt = file.name.replace(/\.[^/.]+$/, '');
                                    var webpName = nameWithoutExt + '.webp';
                                    
                                    var compressedFile = new File([blob], webpName, {
                                        type: 'image/webp',
                                        lastModified: Date.now()
                                    });
                                    resolve(compressedFile);
                                } else {
                                    reject(new Error('WebP conversion failed'));
                                }
                            }, 'image/webp', quality);
                        };
                        
                        img.onerror = function() {
                            reject(new Error('Image loading failed'));
                        };
                        
                        img.src = e.target.result;
                    };
                    
                    reader.onerror = function() {
                        reject(new Error('File reading failed'));
                    };
                    
                    reader.readAsDataURL(file);
                });
            }

            // Index xaric səhifələrin header background şəkilləri — browser compress olmasın
            var NON_HOME_HEADER_BG_FIELDS = [
                'is_about_page_background_image',
                'is_contact_page_background_image',
                'is_project_page_background_image',
                'is_courses_page_background_image',
                'is_tests_page_background_image',
                'is_service_page_background_image',
                'is_footer_background_image',
            ];

            function syncHeaderBgNoCompress() {
                var isNonHomeHeader = NON_HOME_HEADER_BG_FIELDS.some(function(name) {
                    return !!$('input[name="' + name + '"]').prop('checked');
                });
                var $img = $('input[type="file"][name="image"]');
                if (isNonHomeHeader) {
                    $img.attr('data-no-compress', '1');
                } else {
                    $img.removeAttr('data-no-compress');
                }
            }

            NON_HOME_HEADER_BG_FIELDS.forEach(function(name) {
                $(document).on('change', 'input[name="' + name + '"]', syncHeaderBgNoCompress);
            });

            // Şəkil compress handler funksiyası
            function handleImageCompression(e) {
                var $input = $(e.target);
                var inputName = $input.attr('name') || '';
                var inputId = $input.attr('id') || '';

                if ($input.attr('data-no-compress') === '1') {
                    console.log('[Image Compress] Skipping (non-index page header background):', inputName || inputId);
                    return;
                }

                // Əgər artıq işləyirsə, təkrarlanmasın
                if ($input.data('compression-processing')) {
                    return;
                }
                
                var files = e.target.files;
                
                if (!files || files.length === 0) {
                    $input.data('compression-processing', false);
                    return;
                }
                
                // Şəkil fayllarını filtrlə
                var imageFiles = [];
                for (var i = 0; i < files.length; i++) {
                    var file = files[i];
                    
                    // Yalnız şəkil faylları
                    if (!file.type.match(/^image\//)) {
                        continue;
                    }
                    
                    // Əgər artıq WebP-dirsə, dəyişmə
                    if (file.type === 'image/webp') {
                        console.log('[Image Compress] Already WebP, skipping:', file.name);
                        continue;
                    }
                    
                    imageFiles.push(file);
                }
                
                if (imageFiles.length === 0) {
                    $input.data('compression-processing', false);
                    return;
                }
                
                // Processing flag set et
                $input.data('compression-processing', true);
                
                console.log('[Image Compress] Files selected:', imageFiles.length, 'image(s) for', inputName || inputId);
                imageFiles.forEach(function(file) {
                    console.log('[Image Compress] -', file.name, file.type, (file.size / 1024).toFixed(2) + ' KB');
                });
                
                // Progress göstər
                var $progress = $input.siblings('.compress-progress');
                if ($progress.length === 0) {
                    $progress = $('<div class="compress-progress" style="margin-top: 10px; padding: 10px; background: #e3f2fd; border-radius: 4px; border: 1px solid #2196f3;">' +
                        '<div style="font-weight: bold; margin-bottom: 5px; color: #1976d2;">🔄 Şəkillər compress edilir...</div>' +
                        '<div class="compress-info" style="font-size: 12px; color: #666;"></div>' +
                        '<div class="compress-status" style="font-size: 11px; color: #666; margin-top: 5px;"></div>' +
                        '</div>');
                    $input.after($progress);
                }
                
                $progress.show();
                var totalOriginalSize = 0;
                imageFiles.forEach(function(file) {
                    totalOriginalSize += file.size;
                });
                $progress.find('.compress-info').text('Toplam ' + imageFiles.length + ' şəkil seçildi. Original ölçü: ' + (totalOriginalSize / 1024).toFixed(2) + ' KB');
                $progress.find('.compress-status').text('Gözləyin...');
                
                // Bütün şəkilləri paralel compress et (hər birinin uğursuzluğunu ayrıca idarə et)
                var compressPromises = imageFiles.map(function(file, index) {
                    return compressImageToWebP(file, 1920, 1080, 0.8)
                        .then(function(compressedFile) {
                            return { success: true, file: compressedFile, originalFile: file, index: index };
                        })
                        .catch(function(error) {
                            console.error('[Image Compress] Error compressing', file.name, ':', error);
                            return { success: false, error: error, originalFile: file, index: index };
                        });
                });
                
                Promise.all(compressPromises).then(function(results) {
                    var compressedFiles = [];
                    var failedFiles = [];
                    
                    results.forEach(function(result) {
                        if (result.success) {
                            compressedFiles.push(result);
                        } else {
                            failedFiles.push(result);
                        }
                    });
                    
                    console.log('[Image Compress] Compressions done:', compressedFiles.length, 'successful,', failedFiles.length, 'failed');
                    
                    // Yeni FileList yarat - bütün faylları əlavə et
                    var dataTransfer = new DataTransfer();
                    
                    // Əvvəlcə WebP olmayan və ya şəkil olmayan faylları əlavə et
                    for (var i = 0; i < files.length; i++) {
                        var file = files[i];
                        if (!file.type.match(/^image\//) || file.type === 'image/webp') {
                            dataTransfer.items.add(file);
                        }
                    }
                    
                    // Uğursuz olan faylları original halında əlavə et
                    failedFiles.forEach(function(result) {
                        dataTransfer.items.add(result.originalFile);
                        console.log('[Image Compress] Using original (compression failed):', result.originalFile.name);
                    });
                    
                    // Sonra compress edilmiş faylları əlavə et
                    compressedFiles.forEach(function(result) {
                        dataTransfer.items.add(result.file);
                        console.log('[Image Compress] Compressed:', result.file.name, (result.file.size / 1024).toFixed(2) + ' KB');
                    });
                    
                    // File input-u replace et
                    var nativeInput = $input[0];
                    nativeInput.files = dataTransfer.files;
                    
                    console.log('[Image Compress] Files replaced. Total files:', nativeInput.files.length);
                    
                    // Processing flag-i sil
                    $input.data('compression-processing', false);
                    
                    // Məlumat göstər
                    var totalCompressedSize = 0;
                    compressedFiles.forEach(function(result) {
                        totalCompressedSize += result.file.size;
                    });
                    
                    var totalSaved = compressedFiles.length > 0 ? ((1 - totalCompressedSize / totalOriginalSize) * 100).toFixed(1) : '0';
                    var totalSavedKB = ((totalOriginalSize - totalCompressedSize) / 1024).toFixed(2);
                    
                    var statusText = '';
                    if (compressedFiles.length > 0) {
                        statusText += compressedFiles.length + ' şəkil compress edildi:<br>';
                        compressedFiles.forEach(function(result) {
                            var originalSize = (result.originalFile.size / 1024).toFixed(2);
                            var compressedSize = (result.file.size / 1024).toFixed(2);
                            var saved = ((1 - result.file.size / result.originalFile.size) * 100).toFixed(1);
                            statusText += '✅ ' + result.file.name + ': ' + originalSize + ' KB → ' + compressedSize + ' KB (' + saved + '% qənaət)<br>';
                        });
                    }
                    
                    if (failedFiles.length > 0) {
                        statusText += '<br>' + failedFiles.length + ' şəkil compress edilmədi (original istifadə olunur):<br>';
                        failedFiles.forEach(function(result) {
                            statusText += '⚠️ ' + result.originalFile.name + '<br>';
                        });
                    }
                    
                    var infoText = '';
                    if (compressedFiles.length === imageFiles.length) {
                        infoText = '✅ <strong>Bütün şəkillər compress edildi!</strong><br>';
                    } else if (compressedFiles.length > 0) {
                        infoText = '⚠️ <strong>' + compressedFiles.length + ' şəkil compress edildi, ' + failedFiles.length + ' uğursuz oldu</strong><br>';
                    } else {
                        infoText = '❌ <strong>Heç bir şəkil compress edilə bilmədi</strong><br>';
                    }
                    
                    if (compressedFiles.length > 0) {
                        infoText += 'Toplam: ' + (totalOriginalSize / 1024).toFixed(2) + ' KB → ' + (totalCompressedSize / 1024).toFixed(2) + ' KB<br>' +
                            'Ümumi qənaət: ' + totalSaved + '% (' + totalSavedKB + ' KB)';
                    }
                    
                    $progress.find('.compress-info').html(infoText);
                    $progress.find('.compress-status').html(statusText);
                    
                    if (compressedFiles.length === imageFiles.length) {
                        $progress.css({
                            'background': '#e8f5e9',
                            'border-color': '#4caf50'
                        });
                    } else if (compressedFiles.length > 0) {
                        $progress.css({
                            'background': '#fff3e0',
                            'border-color': '#ff9800'
                        });
                    } else {
                        $progress.css({
                            'background': '#ffebee',
                            'border-color': '#f44336'
                        });
                    }
                    
                    setTimeout(function() {
                        $progress.fadeOut();
                    }, 8000);
                }).catch(function(error) {
                    console.error('[Image Compress] Unexpected error:', error);
                    $input.data('compression-processing', false);
                    $progress.find('.compress-info').html(
                        '❌ <strong>Xəta:</strong> ' + error.message + '<br>' +
                        'Original fayllar istifadə olunacaq.'
                    );
                    $progress.find('.compress-status').text('');
                    $progress.css({
                        'background': '#ffebee',
                        'border-color': '#f44336'
                    });
                    setTimeout(function() {
                        $progress.fadeOut();
                    }, 5000);
                });
            }

            // Image field-ləri tap və işlə
            function initImageCompression() {
                $('input[type="file"]').each(function() {
                    var $input = $(this);
                    var inputName = $input.attr('name') || '';
                    var inputId = $input.attr('id') || '';
                    
                    // Əgər artıq event listener var, təkrarlanmasın
                    if ($input.data('compression-initialized')) {
                        return;
                    }
                    
                    $input.data('compression-initialized', true);
                    console.log('[Image Compress] Initialized for:', inputName || inputId);
                });
            }

            // Event delegation - bütün file input-lar üçün işləyir (yeni əlavə edilənlər də daxil)
            $(document).on('change', 'input[type="file"]', handleImageCompression);

            // MutationObserver - yeni əlavə edilən file input-ları avtomatik tapır
            function setupMutationObserver() {
                if (typeof MutationObserver === 'undefined') {
                    console.warn('[Image Compress] MutationObserver not supported');
                    return;
                }
                
                var observer = new MutationObserver(function(mutations) {
                    var foundNewInputs = false;
                    mutations.forEach(function(mutation) {
                        mutation.addedNodes.forEach(function(node) {
                            if (node.nodeType === 1) { // Element node
                                var $node = $(node);
                                // Yeni əlavə edilən file input-ları tap
                                var $inputs = $node.find('input[type="file"]').add($node.filter('input[type="file"]'));
                                if ($inputs.length > 0) {
                                    foundNewInputs = true;
                                }
                            }
                        });
                    });
                    
                    if (foundNewInputs) {
                        // Qısa gecikmə ilə yeni input-ları initialize et
                        setTimeout(function() {
                            initImageCompression();
                        }, 100);
                    }
                });
                
                // Bütün səhifəni izlə
                observer.observe(document.body, {
                    childList: true,
                    subtree: true
                });
                
                console.log('[Image Compress] MutationObserver initialized');
            }

            // Django admin ready - BÜTÜN KOD IIFE İÇİNDƏ
            $(document).ready(function() {
                console.log('[Image Compress] Script loaded');

                syncHeaderBgNoCompress();

                // İlkin initialization
                setTimeout(function() {
                    initImageCompression();
                }, 500);
                
                // MutationObserver işə sal
                setupMutationObserver();
                
                // Inline formlar üçün (əlavə təhlükəsizlik)
                $(document).on('formset:added', function() {
                    setTimeout(function() {
                        syncHeaderBgNoCompress();
                        initImageCompression();
                    }, 200);
                });
            });
            
        })($); // jQuery-ni parametr kimi ötürürük - scope təhlükəsizdir
    }
    
    // Script-i işə sal
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', startScript);
    } else {
        startScript();
    }

})();
