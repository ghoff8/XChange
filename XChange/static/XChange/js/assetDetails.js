function calculate() {
		var currentPrice = document.getElementById('currentPrice').innerHTML;	
		var quantity = document.getElementById('numOfShares').value;
		var result = document.getElementById('totalCost');	
		var myResult = currentPrice * quantity;
		console.log(quantity, currentPrice)
		result.textContent= '$' + myResult;
      
		
	}