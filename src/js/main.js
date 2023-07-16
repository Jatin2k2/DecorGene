const uploadFile = () => {
    const fileInput = document.querySelector('#file-input');
    const file = fileInput.files[0];
    
    const formData = new FormData();
    formData.append('file', file);
    
    fetch('/upload', {
      method: 'POST',
      body: formData
    })
    .then(response => {
      if (response.ok) {
        return response.json();
      } else {
        throw new Error('File upload failed');
      }
    })
    .then(data => {
      console.log(data);  // Process success response
    })
    .catch(error => {
      console.error(error);  // Handle error response
    });
  }
  