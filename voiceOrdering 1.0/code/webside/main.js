//這邊必須要async funciton 因為python返回需要時間，而JS 又不會block，
//所以需要用async function 加上await去呼叫PY function
let note_id = document.getElementById('note')
let ordering_id = document.getElementById('ordering')

async function btn_recommend(){
    document.getElementById('recommendation').textContent = await eel.recommendation_system()()
}

async function btn_add_order(){ //按下新增餐點按鈕
    
    //顯示目前狀態
    document.getElementById('state').textContent = await eel.add_order(note_id.value)()

    //將餐點加入alert條中
    var wrapper = document.createElement('div')
    wrapper.innerHTML = '<div class="alert alert-primary alert-dismissible" role="alert">' + note_id.value + '</div>'
    ordering_id.append(wrapper)

    document.getElementById('price').textContent = await eel.now_order()() //呼叫python function，更新顯示購物車資訊
    note_id.value = ""
}

async function btn_record(){ //按下語音點餐按鈕
    document.getElementById('state').textContent = "請開始語音點餐"
    note_id.value = "" //清空輸入欄
    note_id.value = await eel.order_meal()() //呼叫python function，將語音輸入輸入欄
    document.getElementById('state').textContent = "語音點餐完成"
}

async function btn_finished(){ //按下完成點餐按鈕
    await eel.finished()() //呼叫python function

    //reset
    note_id.value = ""
    document.getElementById('price').textContent = "" //將顯示的購物車資訊刪除
    while (ordering_id.firstChild) { //將所有餐點alert刪除
        ordering_id.removeChild(ordering_id.firstChild)
    }
    document.getElementById('state').textContent = "請開始點餐"
    window.confirm('點餐完成')
}

async function btn_reset(){ //按下重置已點餐點按鈕
    await eel.reset()() //呼叫python function
    note_id.value = ""
    document.getElementById('price').textContent = "" //將顯示的購物車資訊刪除
    while (ordering_id.firstChild) { //將所有餐點alert刪除
        ordering_id.removeChild(ordering_id.firstChild)
    }
    document.getElementById('state').textContent = "購物車已清空"
}
