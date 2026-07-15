$('#translatorRequestModal').on('show.bs.modal', function(e){
    if (typeof e.relatedTarget !== 'undefined') {
        var target = e.relatedTarget;
    }
    else {
        var target = $('#addLanguage :selected').get(0);
    }

    $('#requestLanguageName').text(target.dataset.language);
    $('#requestLanguageName').attr('lang', target.dataset.code);
    $('#requestLanguageCode').text(target.dataset.code);
    $('#requestLanguageCodeInput').val(target.dataset.code);
    $('#requestResult').hide();
    $('#requestFields, #requestSubmit').show();
    $('#translatorRequestModal input, #translatorRequestModal textarea').prop('disabled', false);
});

$('#addLanguage').change(function(e){
    if ($(this).find(':selected').attr('data-url')) {
        window.location = $(this).find(':selected').attr('data-url');
    }
    else {
        $('#translatorRequestModal').modal('show');
    }
});

$('#translatorRequestModal form').submit(function(e) {
    e.preventDefault();
    const form = $(this);
    if (form.find('textarea').val() == '') {
        return;
    }
    form.find('input, textarea').prop('disabled', true);
    $.ajax({
        url: form.attr('action'),
        data: {
            explanation: form.find('[name=explanation]').val(),
            language: form.find('[name=language]').val(),
            csrfmiddlewaretoken: form.find('[name=csrfmiddlewaretoken]').val(),
        },
        method: "POST",
        dataType: "json",
        success: function(data) {
            $('#requestResult').text(data['message']).show();
            $('#requestFields, #requestSubmit').hide();
            $('#languagerow-' + form.find('[name=language]').val() + ' button').replaceWith(data['button']);
            form.find('[name=explanation]').val('');
            $('#addLanguage option:first-child').prop('selected', true);
        }
    });
});