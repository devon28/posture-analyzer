var coordinates = [];
var canvas;
var ctx;
var image;

function initCanvas() {
  canvas = document.getElementById('display_canvas');
  ctx = canvas.getContext('2d');

  var imageInput = document.getElementById('image_input');
  imageInput.addEventListener('change', handleImageUpload);

  canvas.addEventListener('click', handleClick);
}

function handleImageUpload(event) {
  image = new Image();
  image.onload = function() {
    canvas.width = image.width;
    canvas.height = image.height;
    ctx.drawImage(image, 0, 0);
  };

  var file = event.target.files[0];
  var reader = new FileReader();
  reader.onload = function(event) {
    image.src = event.target.result;
  };
  reader.readAsDataURL(file);
}

function handleClick(event) {
  // Extract coordinates
  var rect = canvas.getBoundingClientRect();
  var scaleX = canvas.width / rect.width;
  var scaleY = canvas.height / rect.height;
  var x = (event.clientX - rect.left) * scaleX;
  var y = (event.clientY - rect.top) * scaleY;

  // Store coordinates in array
  coordinates.push({ x: x, y: y });

  // Draw line between coordinates
  drawLine();

  // Update form display
  updateFormDisplay();
}

function removeLastCoordinate() {
  if (coordinates.length > 0) {
    coordinates.pop(); // Remove the last coordinate from the array
    drawImage(); // Redraw the image
    drawLine(); // Redraw the lines
    updateFormDisplay();
  }
}

function drawImage() {
  ctx.drawImage(image, 0, 0);
}

function drawLine() {
  // Clear the canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Redraw the image
  drawImage();

  // Draw lines between coordinates
  ctx.beginPath();
  ctx.moveTo(coordinates[0].x, coordinates[0].y);
  for (var i = 1; i < coordinates.length; i++) {
    ctx.lineTo(coordinates[i].x, coordinates[i].y);
  }
  ctx.stroke();
}

function updateFormDisplay() {
  var formDisplay = document.getElementById('form-display');
  formDisplay.innerHTML = '';

  var bodyParts = {
    'Ear': 0,
    'Neck Base': 1,
    'Upper Back': 2,
    'Low Back': 3,
    'Hip Joint': 4,
    Knee: 5,
    Ankle: 6,
  };

  var coordinateDict = {}; // Create an empty dictionary to store the coordinates

  // Display checkmark instead of coordinates
  for (var i = 0; i < coordinates.length; i++) {
    var position = Object.keys(bodyParts)[i];
    var coordinateString = position + ': &#10003;'; // Checkmark symbol
    

    // Store coordinates as key-value pair in the dictionary
    coordinateDict[position] = [coordinates[i].x, coordinates[i].y];
  }

  // Convert the dictionary to a JSON string and set it as the value of a hidden input field
  var coordinateJSON = JSON.stringify(coordinateDict);
  formDisplay.innerHTML +=
    '<input type="hidden" name="coordinateJSON" value=\'' +
    coordinateJSON +
    '\'>';
}


function submitForm(event) {
  event.preventDefault(); // Prevent the default form submission

  // Create a hidden input field to store the coordinate dictionary as JSON
  var coordinateInput = document.createElement('input');
  coordinateInput.type = 'hidden';
  coordinateInput.name = 'coordinateJSON';
  coordinateInput.value = JSON.stringify(getCoordinateDictionary());

  // Append the hidden input field to the form
  var form = document.querySelector('form');
  form.appendChild(coordinateInput);

  // Convert the canvas content to a data URL
  var imageDataURL = canvas.toDataURL('image/png');

  // Create a hidden input field to store the image data URL
  var imageInput = document.createElement('input');
  imageInput.type = 'hidden';
  imageInput.name = 'imageDataURL';
  imageInput.value = imageDataURL;

  // Append the hidden input field to the form
  form.appendChild(imageInput);

  // Submit the form
  form.submit();
}

function getCoordinateDictionary() {
  var bodyParts = {
    'Ear': 0,
    'Neck Base': 1,
    'Upper Back': 2,
    'Low Back': 3,
    'Hip Joint': 4,
    Knee: 5,
    Ankle: 6,
  };

  var coordinateDict = {};

  for (var i = 0; i < coordinates.length; i++) {
    var coordinate = coordinates[i];
    var position = Object.keys(bodyParts)[i];
    coordinateDict[position] = [coordinate.x, coordinate.y];
  }

  return coordinateDict;
}

function toggleDiv(data) {
  var div = document.getElementById(data);
  if (div.style.display === 'none') {
    div.style.display = 'block';
  } else {
    div.style.display = 'none';
  }
}

let clickCount = 0;
      let backCount = 0;

      function toggleCheck(index) {
        const part = document.getElementById(`part${clickCount + 1}`);
        const isChecked = part.classList.toggle("checked");

        if (isChecked) {
          part.innerHTML = "<span class='checkmark'>✔</span>";
          clickCount++;
        } else {
          part.innerHTML = "";
          clickCount--;
        }

        updateSubmitButton();
      }

      function removeLastCoordinate() {
        if (clickCount > 0) {
          const part = document.getElementById(`part${clickCount}`);
          part.classList.remove("checked");
          part.innerHTML = "";
          clickCount--;
        }

        backCount++;

        updateSubmitButton();
      }

      function updateSubmitButton() {
        const submitButton = document.getElementById("submitButton");
        submitButton.disabled = clickCount < (7 - backCount);
      }