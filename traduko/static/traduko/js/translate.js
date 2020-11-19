function setup_translation_events() {
    $('.translate-button').click(function(e) {
        $(this).hide();
        $(this).parents('.translation-row').find('.translation-form').removeClass('d-none').show();
        $(this).parents('.translation-row').find('textarea').focus();
    });

    $('.translated-text').click(function(e) {
        e.preventDefault();
        $(this).hide();
        $(this).parents('.translation-row').find('.translation-form').removeClass('d-none').show();
        $(this).parents('.translation-row').find('textarea').focus();
    });

    $('.translate-cancel').click(function() {
        $(this).parents('.translation-row').find('.translate-button').show();
        $(this).parents('.translation-row').find('.translated-text').show();
        $(this).parents('.translation-row').find('.translation-form').hide();
    });

    $('.translation-form').submit(function(e) {
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
            },
            method: "POST",
            dataType: "html",
            success: function(data) {
                form.parents('.translation-row').replaceWith(data);
                setup_translation_events();
            }
        });
    });

    $('.dropdown-language-menu a').click(function(e){
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
//                original_text.css('opacity', '1');
            }
        });
    });

    $('.markoutdated, .marktranslated').click(function(e){
        e.preventDefault();
        const translated = $(this).hasClass('marktranslated');
        if (window.confirm('Ĉu vi certe volas marki ĉi tiun ĉenon kiel ' + (translated ? 'tradukitan' : 'retradukendan') + '?')) {
            const row = $(this).parents('.translation-row');
            $.ajax({
                url: $(this).attr('data-url'),
                method: "GET",
                dataType: "html",
                success: function(data) {
                    row.replaceWith(data);
                    setup_translation_events();
                }
            });
        }
    });
}
setup_translation_events();

/*window.addEventListener('beforeunload', function(e){
if ($('.translation-form:visible').length > 0) {
        e.preventDefault();
        e.returnValue = '';
        return;
    }
    delete e['returnValue'];
});*/