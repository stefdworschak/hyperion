$(document).ready(function(){

    let $toggle = $('.card-record-toggle');
    let heights = [];
    $toggle.each(function(i){
        heights.push($(this).height());
    })
    console.log(heights)
    let $add_record = $('#new_patient_record');
    let $headers = $('.card-header');

    $add_record.click(function(){
        $toggle.animate({height:'0px', padding:'0px'})
        $toggle.addClass('overflow_hidden');

        $headers.click(function(){
            console.log("Clicked")
            console.log($toggle.height())
            if($toggle.height() == 0){
                $toggle.each(function(i){
                    $(this).animate({height: heights[i]+40+'px', padding: '20px'})
                })
               
            }
        })
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

})