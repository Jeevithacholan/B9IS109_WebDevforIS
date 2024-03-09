
// Filter Js
$(document).ready(function () {

  $(function () {
    $('[data-toggle="tooltip"]').tooltip()
  });

  $(".filter-item").click(function () {
    const value = $(this).attr("data-filter");
    if (value == "all") {
      $(".post-box").show("1000");
    } else {
      $(".post-box")
        .not("." + value)
        .hide("1000");
      $(".post-box")
        .filter("." + value)
        .show("1000");
    }
  });
  // Add active to btn
  $(".filter-item").click(function () {
    $(this).addClass("active-filter").siblings().removeClass("active-filter");
  });
});
// Header BackGround Change On Scroll
let header = document.querySelector("header");

window.addEventListener("scroll", () => {
  header.classList.toggle("shadow", window.scrollY > 0);
})
//search
function productSearch() {
  var searchBar = event.currentTarget.value;
  document.querySelectorAll(".post div").forEach((product)=>{
      product.classList.remove("d-none")
      if (product.querySelector("a").innerHTML.toLowerCase().indexOf(searchBar.toLowerCase()) == -1) {
        product.classList.add("d-none")
      }

  })
}

function triggerBtnClick(productId) {
    location.href = "/reservation/" + productId;
}

