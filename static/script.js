$.getJSON("/static/index.json", function(json) {
		index_data = json
	})
	let added_col_count = 0

    let input = document.querySelector('#stock_id')
    let submit = document.querySelector('#submit_id')
    let output = document.querySelector('#output_html')

	function add_text_field(interested_items){
		interested_items.forEach(function(value, index) {
			let added_element = `<p><input type='text' value=${value} id=int_col_${added_col_count} class='interested_items_col_input'>
									<button class="rm_btn" type="submit" id="rm_col_${added_col_count}">移除欄位</button></p>`
			$("#interested_items_col_div").append(added_element)
			added_col_count += 1
		})
	}

	$("#select").change(function () {
	  let select_item = $("#select option:selected").text()
	  let tmp = document.getElementById("selected_result")
	  tmp.innerText = `${select_item} 預設的欄位有:`
	  	const interested_items = index_data[select_item].interested_item
		$("#interested_items_col_div").empty()
	  	add_text_field(interested_items)
	  	$("#add_col_button").empty()
	  	$("#add_col_button").append('<button type="submit" id="add_col" name="add_col">增加欄位</button>')
	  	$("#submit_button").empty()
	  	$("#submit_button").append(`<button type="submit" id="submit" name="submit">取得${select_item}作圖</button>`)
	})


	$('#interested_items_col_div').on('click','.rm_btn', function(){
		$(this).remove()
		txt_id = this.id.replace("rm_col_", 'int_col_')
		document.getElementById(txt_id).remove()
    })

	$(document).on('click',"#add_col", function(){
		add_text_field(['請填入'])
    })


	$(document).on('click',"#submit_button", function(){
		let int_item_list = $('.interested_items_col_input').map(function() {
																return $(this).val()
															}).toArray()
		let select_item = $("#select option:selected").text()
		let stock_id = input.value
		$("#error_display").text('')
		fetch('http://localhost:9999/search', {
			method: 'POST',
			body: JSON.stringify({stock_id: stock_id,
								  select_item: select_item,
								  int_item_list: int_item_list})
			})
		.then(res => res.json())
		.then(function(data) {
           $("#error_display").text(data['error'])
        })
    })