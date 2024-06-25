function getSelectedValue() {
    const userText = document.getElementById('userText').value;
    const userSelection = document.getElementById('userSelection').value;
    
    let selectedValue;
    if (userText) {
      selectedValue = userText; // User entered their own value
    } else if (userSelection) {
      selectedValue = userSelection; // User chose from the dropdown
    } else {
      selectedValue = "No selection made";
    }
    
    alert("Selected value: " + selectedValue);
  }