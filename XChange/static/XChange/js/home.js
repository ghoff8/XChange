function openAsset(buttonName) {
    var x;
    var y = document.getElementsByClassName("assetDiv");
    for (x = 0; x < y.length; x++) {
        y[x].style.display = "none";
    }
    document.getElementById(buttonName).style.display = "block";
}

