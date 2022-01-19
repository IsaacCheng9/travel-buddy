document.querySelectorAll(".checkbox").forEach(function(checkbox) {
	checkbox.onclick = function() {
		this.classList.toggle("checked");
	}
});