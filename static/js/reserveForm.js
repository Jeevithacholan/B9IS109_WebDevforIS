$("#formValidation").validate({
  rules:{
    name:{
    minlength: 2
    },
    email:true
  },
  phone:{
    number:true,
    minlength: 10,
    maxlength: 10
  },
  messages: {
    name:{
      required: "Please Enter Your Name",
      minlength: "Name at least 2 characters"
    },
    email:"Please Enter Your Email ID",
    phone:"Please Enter Your Contact Number",
    formMessage: "Please Enter Your Message"
  },

  submitHandler: function(form) {
  alert("Reserving your product");
  var productId = getProductID();
  // Redirect to reservation confirmation page
  location.href = "/reservationConfirmation/" + productId;
}
});

function getProductID() {
  // Retrieve the product ID from the hidden input field
  var productId = document.getElementById("product_id").value;
  return productId;
}
