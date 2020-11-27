const csrf = $('#csrf').val();

function setup_translation_events() {
    $('.translate-button').off('click').click(function(e) {
        $(this).hide();
        const row = $(this).parents('.translation-row');
        row.find('.translation-form').removeClass('d-none').show();
        row.find('textarea').focus();
    });

    $('.translated-text').off('click').click(function(e) {
        e.preventDefault();
        $(this).hide();
        const row = $(this).parents('.translation-row');
        row.find('.translation-form').removeClass('d-none').show();
        row.find('textarea').focus();
    });

    $('.translate-cancel').off('click').click(function() {
        const row = $(this).parents('.translation-row');
        row.find('.translate-button').show();
        row.find('.translated-text').show();
        row.find('.translation-form').hide();
        row.find('.translate-button, .translate-text').focus();
    });

    $('.translation-form').off('submit').submit(function(e) {
        e.preventDefault();
        const form = $(this);
        if (form.find('textarea').val() == '') {
            return;
        }
        form.find('input').prop('disabled', true);
        $.ajax({
            url: form.attr('action'),
            data: {
                text: JSON.stringify(form.find('textarea').serializeArray()),
                context: form.find('[name=context]').val(),
                minor: form.find('.minor-change').is(':checked'),
                pluralized: form.find('.pluralized').is(':checked'),
                csrfmiddlewaretoken: csrf
            },
            method: "POST",
            dataType: "html",
            success: function(data) {
                form.parents('.translation-row').replaceWith(data);
                setup_translation_events();
                form.find('.translate-button, .translate-text').focus();
            }
        });
    });

    $('.dropdown-language-menu a').off('click').click(function(e){
        e.preventDefault();
        const original_text = $(this).parents('.translation-row').find('.original-text');
        original_text.css('opacity', '.7');
        $(this).parents('.dropdown').find('.dropdown-toggle').text($(this).text());

        $.ajax({
            url: $(this).attr('href'),
            method: "GET",
            dataType: "html",
            success: function(data) {
                original_text.replaceWith(data);
            }
        });
    });

    $('.markoutdated, .marktranslated').off('click').click(function(e){
        e.preventDefault();
        const translated = $(this).hasClass('marktranslated');
        if (window.confirm('Ĉu vi certe volas marki ĉi tiun ĉenon kiel ' + (translated ? 'tradukitan' : 'retradukendan') + '?')) {
            const row = $(this).parents('.translation-row');
            $.ajax({
                url: $(this).attr('data-url'),
                method: "POST",
                data: {
                    csrfmiddlewaretoken: csrf
                },
                dataType: "html",
                success: function(data) {
                    row.replaceWith(data);
                    setup_translation_events();
                }
            });
        }
    });

    $('.deletestring').off('click').click(function(e){
        e.preventDefault();
        if (window.confirm('Ĉu vi certe volas forigi ĉi tiun ĉenon?')) {
            const row = $(this).parents('.translation-row');
            $.ajax({
                url: $(this).attr('data-url'),
                method: "POST",
                data: {
                    csrfmiddlewaretoken: csrf
                },
                dataType: "html",
                success: function(data) {
                    row.replaceWith('<div class="alert alert-success">' + data + '</div>');
                }
            });
        }
    });

    $('.show-history').off('click').click(function(e){
        e.preventDefault();
        const historyElement = $(this).parents('.translation-author').find('.old-versions');

        if (historyElement.is(':visible')) {
            historyElement.hide();
        }
        else {
            historyElement.removeClass('d-none').show();
            if (historyElement.find('.old-version.load').length > 0) {
                const href = $(this).attr('href');
                $.ajax({
                    url: href,
                    method: "GET",
                    dataType: "html",
                    success: function(data) {
                        historyElement.html(data);
                        setup_translation_events();
                    }
                });
            }
        }
    });

    $('.toggleDeletedText').off('click').click(function(e){
        const historyElement = $(this).parents('.old-versions');
        if (historyElement.find('del:visible').length > 0) {
            historyElement.find('del').hide();
        }
        else {
            historyElement.find('del').show();
        }
    });
}
setup_translation_events();

var post_new_string = false;
$('#new-string-form').submit(function(){
    post_new_string = true;
});

$('#new-string-form').removeClass('d-none').hide();
$('#new-string-form-show').click(function(){
    $('#new-string-form').show();
    $('#new-string-form-show').hide();
    $('html, body').animate({
        scrollTop: ($('#new-string-form').offset().top)
    },200);
});
$('#new-string-form-hide').click(function(){
    $('#new-string-form').hide();
    $('#new-string-form-show').show();
});

window.addEventListener('beforeunload', function(e){
    if ($('.translation-form:visible').length > 0 || ($('#new-string-text').is(':visible') && $('#new-string-text').val() != '' && !post_new_string)) {
        e.preventDefault();
        e.returnValue = '';
        return;
    }
    delete e['returnValue'];
});
