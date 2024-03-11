
$(document).ready(function () {

 document.getElementById('update_button').addEventListener('click', function() {
        document.querySelectorAll('.product-name-description').forEach(icon => {
            const productId = icon.getAttribute('data-product-id');
            const productName = document.getElementById(`product_name_${productId}`);
            const productDescription = document.getElementById(`product_description_${productId}`);

                    // Check if elements are already input fields
                if (productName.querySelector('input') === null) {
                    // Replace the text with input fields
                    productName.innerHTML = `<input type="text" class="form-control" name="product_name_${productId}" value="${productName.textContent}">`;
                    productDescription.innerHTML = `<input type="text" class="form-control" name="product_description_${productId}" value="${productDescription.textContent}">`;
                }
            });

            document.getElementById('product_form').submit();
        });

 document.querySelectorAll('.edit-icon').forEach(icon => {
        icon.addEventListener('click', function() {
            const productId = this.getAttribute('data-product-id');
            const productName = document.getElementById(`product_name_${productId}`);
            const productDescription = document.getElementById(`product_description_${productId}`);

            // Check if elements are already input fields
            if (productName.querySelector('input') === null) {
                // Replace the text with input fields
                productName.innerHTML = `<input type="text" class="form-control" name="product_name_${productId}" value="${productName.textContent}">`;
                productDescription.innerHTML = `<input type="text" class="form-control" name="product_description_${productId}" value="${productDescription.textContent}">`;
            }
        });
    });
});