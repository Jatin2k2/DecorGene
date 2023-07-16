function readURL(input) {
    if (input.files && input.files[0]) {
      var reader = new FileReader();

      reader.onload = function(e) {
        $('.image-upload-wrap').hide();
        $('.file-upload-image').attr('src', e.target.result);
        $('.file-upload-content').show();
        $('.image-title').html(input.files[0].name);
      };

      reader.readAsDataURL(input.files[0]);
    } else {
      removeUpload();
    }
  }

  function removeUpload() {
    $('.file-upload-input').replaceWith($('.file-upload-input').clone());
    $('.file-upload-content').hide();
    $('.image-upload-wrap').show();
  }

  $(document).ready(function() {
    $('.image-upload-wrap').bind('dragover', function() {
      $('.image-upload-wrap').addClass('image-dropping');
    });

    $('.image-upload-wrap').bind('dragleave', function() {
      $('.image-upload-wrap').removeClass('image-dropping');
    });
  });

  function submitUpload() {
    var fileInput = document.querySelector('.file-upload-input');
    var file = fileInput.files[0];
    
    if (!file) {
      console.error('No file selected');
      return;
    }
    
    var formData = new FormData();
    formData.append('file', file);
    
    fetch('/', {
      method: 'POST',
      body: formData
    })
    .then(response => {
      if (response.ok) {
        return response.json();
      } else {
        throw new Error('Error submitting image');
      }
    })
    .then(data => {
      if (data.error) {
        console.error(data.error);
        // Handle the error by displaying a message or taking appropriate action
      } else {
        console.log(data.message); // Process success response
        window.location.href = '/getRecommendation';
        // Add your desired logic here after the successful submission
      }
    })
    .catch(error => {
      console.error(error); // Handle error response
      // Add your error handling logic here
    });
  }
  