$(document).ready(function(){
    $("#send_answer_btn").click(function(){
        $.post("/user-answer",
        {
          user_answer: $('#user_answer').val()
        },
        function(data,status){
            // using jquery
            $('#fcard').attr('src', '/static/pics/a_tear.jpg')
            // using javascript
            //document.getElementById('fcard').src='/static/pics/a_tear.jpg';
            //alert('Your saved answer: ' + data + '\nWhas it saved? ' + status );
        });
    });
});

/*$(document).ready(function(){
    $("#test_btn").click(function(){
        $.post("/user-answer",
        {
          name: "Donald Duck",
          city: "Duckburg"
        },
        function(data,status){
            alert("Data: " + data + "\nStatus: " + status);
        });
    });
});*/

/*$(document).ready(function(){
    $("#test_btn").click(function(){
        alert("Value: " + $("#user_answer").val());
    });
});*/
