// Garante que o código só rode se o jQuery do Django estiver disponível.
if (window.django && window.django.jQuery) {
    (function($) {
        // Espera o documento estar completamente carregado.
        $(document).ready(function() {
            // 1. Mapeia os elementos do formulário que vamos manipular.
            const sentCheckbox = $('#id_ifo_sent');
            const sentDateRow = $('.form-row.field-ifo_sent_date');
            
            const discardedCheckbox = $('#id_ifo_discarded');
            const discardedDateRow = $('.form-row.field-ifo_discarded_date');

            // 2. Cria uma função reutilizável para mostrar/esconder os campos.
            function toggleDateFields() {
                // Lógica para o campo de data de envio
                if (sentCheckbox.is(':checked')) {
                    sentDateRow.slideDown('fast'); // Mostra com uma animação suave
                } else {
                    sentDateRow.slideUp('fast');   // Esconde com uma animação suave
                }

                // Lógica para o campo de data de descarte
                if (discardedCheckbox.is(':checked')) {
                    discardedDateRow.slideDown('fast');
                } else {
                    discardedDateRow.slideUp('fast');
                }
            }

            // 3. Executa a função uma vez quando a página carrega,
            //    para definir o estado inicial correto.
            toggleDateFields();

            // 4. Adiciona "escutadores" de eventos. A função será chamada
            //    toda vez que o estado de um dos checkboxes mudar.
            sentCheckbox.on('change', toggleDateFields);
            discardedCheckbox.on('change', toggleDateFields);
        });
    })(django.jQuery);
}
