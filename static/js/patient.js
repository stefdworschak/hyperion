$(document).ready(function(){

    let $toggle = $('.card-record-toggle');
    let heights = [];
    $toggle.each(function(i){
        heights.push($(this).height());
    })
    let $add_record = $('#new_patient_record');
    let $cancel_add = $('#cancel_new_patient_record');
    let $add_appointment = $('#new_patient_appointment');
    let $cancel_add_appointment = $('#cancel_new_patient_appointment');

    let $headers = $('.card-header:not(.add-header)');

    $add_record.click(function(){
        $add_record.hide();
        $toggle.animate({height:'0px', padding:'0px'})
        $toggle.addClass('overflow_hidden');

        $headers.click(function(){
            if($toggle.height() == 0){
                $toggle.each(function(i){
                    $(this).animate({height: heights[i]+40+'px', padding: '20px'});
                })
               
            }
        })

        $('.add-new-patient-record').show();
        $('.card-body.session-list ul li').removeClass('active-session-link');
        $('.card-body.session-list ul li').first()
                .addClass('active-session-link');
        let shown_item = $('.active-session-card');
        shown_item.removeClass('active-session-card')
            .addClass('inactive-session-card');
        $cancel_add.show();
    })

    $cancel_add.click(function(){
        let not_shown_item = $('.inactive-session-card');
        not_shown_item.first().removeClass('inactive-session-card')
            .addClass('active-session-card');
        $('.add-new-patient-record').hide();
        if($toggle.height() == 0){
            $toggle.each(function(i){
                $(this).animate({height: heights[i]+40+'px', padding: '20px'});
            })
            
        }
        $cancel_add.hide();
        $add_record.show();
    })

    $add_appointment.click(function(){
        $add_appointment.hide();
        $cancel_add_appointment.show()
        $('.add-new-patient-appointment').show();

    })

    $cancel_add_appointment.click(function(){
        $cancel_add_appointment.hide();
        $add_appointment.show();
        $('.add-new-patient-appointment').hide();
    })

    let $file = $('#fileupload');
    $file.on('change', function(e){
        var files = e.currentTarget.files;
        for (let x in files) {
            var filesize = ((files[x].size/1024)/1024).toFixed(4);
            
        }
    })

    let $form = $('#createDocumentForm');
    $form.submit(function(e){
        let errors = [];
        var files = $('#fileupload')[0].files;
        for (let x in files) {
            var filesize = ((files[x].size/1024)/1024).toFixed(4);
            if(filesize > 30){
                errors.push("<li>One or more files are too big. Only files up to 30MB allowed.</li>");
            }
        }
        if(files.length > 10){
            errors.push("<li>The max. file uploads are 10. Pleare remove some files or zip them.</li>");
        }
        if(errors.length > 0){
            $('#create_document_errors').html(`<ul class="alert alert-danger">${errors.join("")}</ul>`);
            $('#create_document_errors ul').append()
            e.preventDefault();
        } else {
            $('#create_document_errors').html("");
        }
    })

    $('.card-body.session-list ul li').click(function(){
        $('.add-new-patient-record').hide();
        $('.card-body.session-list ul li').removeClass('active-session-link');
        $(this).addClass('active-session-link');
        let session_id = $(this).find('a').data('id');
        let shown_item = $('.active-session-card');
        shown_item.removeClass('active-session-card')
            .addClass('inactive-session-card');
        $(`.session_${session_id}`).removeClass('inactive-session-card')
            .addClass('active-session-card');

    })

})