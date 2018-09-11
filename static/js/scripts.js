function playAudioOut() {
    var audio_out=document.getElementById('card_audio');
    audio_out.play();
}

$(document).ready(function(){
    $("#send_answer_btn").click(function(){
        $.post("/user-answer",
        {
          user_answer: $('#user_answer').val()
        },
        function(data,status){
            // using jquery
            $('#fcard').attr('src', 'static/pics/a_tear.jpg')
        });
    });
});

//the pure JS implementation for getting the next flashcard picture
//currently, i'ts not used -- the jquery implementation is used instead
function new_pic() {
    var pic=document.getElementById('fcard');
    pic.setAttribute('src', 'static/pics/a_tear.jpg');
}

var default_title="Let's Practice";

function setTitlePractise() {
          var lang=document.getElementById("lang_select").value;
          document.getElementById("title_practice").innerHTML=default_title + " " + lang + "!";
      }

function updateTitlePractise() {
    var lang=document.getElementById("lang_select").value;
    document.getElementById("title_practice").innerHTML=default_title + " " + lang + "!";
}
