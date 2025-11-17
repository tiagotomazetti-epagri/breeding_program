// Garante que o script só rode se o jQuery do Django estiver disponível.
if (window.django && window.django.jQuery) {
    (function($) {
        // Usamos o evento 'load' para garantir que todos os widgets do admin,
        // incluindo os de autocomplete (select2), já foram renderizados.
        $(window).on('load', function() {
            
            const isEpagriCheckbox = $('#id_is_epagri_material');
            
            // Se a checkbox não estiver na página, o script não faz nada.
            if (!isEpagriCheckbox.length) {
                return;
            }

            // Encontra os 'form-rows' que contêm nossos campos.
            // Esta é a maneira mais robusta de selecionar os elementos.
            const populationRow = $('.form-row.field-population');
            const motherRow = $('.form-row.field-mother');
            const fatherRow = $('.form-row.field-father');
            const mutatedFromRow = $('.form-row.field-mutated_from');

            function toggleGenealogyFields() {
                // Se a checkbox "É material do programa?" estiver marcada...
                if (isEpagriCheckbox.is(':checked')) {
                    populationRow.show(); // Mostra o campo 'população'
                    motherRow.hide();     // Esconde os outros
                    fatherRow.hide();
                    mutatedFromRow.hide();
                } else {
                    // Se não estiver marcada...
                    populationRow.hide(); // Esconde o campo 'população'
                    motherRow.show();     // Mostra os outros
                    fatherRow.show();
                    mutatedFromRow.show();
                }
            }

            // --- Event Listeners ---

            // Executa a função uma vez quando a página carrega para definir o estado inicial.
            toggleGenealogyFields();

            // Adiciona um "ouvinte" que executa a função toda vez que a checkbox é alterada.
            isEpagriCheckbox.on('change', toggleGenealogyFields);
        });
    })(django.jQuery);
}
