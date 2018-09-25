function playAudioOut() {
    var audio_out=document.getElementById('card_audio');
    audio_out.play();
}

$(document).ready(function() {
    $("#lang_select").change( function() {
        $.get("/change-language",
                {
                    language : $("#lang_select").val()
                },
                function(data) {
                    alert(data);
                }
        );

    });

});


// submit user's answer and go to next picture
// $(document).ready(function(){
//   $("#send_answer_btn").click(function(){
//       $.post("/",
//       {
//         user_answer: $('#user_answer').val()
//       },
//       function(data,status){
//         $('#fcard').attr('src', 'static/pics/HD/actress-beauty-face-girl-head.svg')
//       });
//   });
// });

// submit user's answer and go to next picture
// $(document).ready(function(){
//   $("#send_answer_btn").click(function(){
//       $.post("/",
//       {
//         user_answer: $('#user_answer').val()
//     });
//   });
// });

//the pure JS implementation for getting the next flashcard picture
//currently, i'ts not used -- the jquery implementation is used instead
// function new_pic() {
//     var pic=document.getElementById('fcard');
//     pic.setAttribute('src', 'static/pics/HD/apple.jpg');
// }

// updating current_language
// $(document).ready(function(){
//     var language = $('#lang_select').val()
//     $("#lang_select").change(function(){
//         $.post("/",
//         {
//           current_language: language
//         },
//         function(){
//             // update the title with the new langauge choice
//             language = language.charAt(0).toUpperCase() + language.substr(1)
//             document.getElementById("title_practice").innerHTML=default_title + " " + language + "!"
//         });
//     });
// });


var default_title="Let's Practice";

function title_cap(word) {
    return word.charAt(0).toUpperCase() + word.substr(1)
}

function setTitlePractise() {
          var lang=document.getElementById("lang_select").value;
          document.getElementById("title_practice").innerHTML=default_title + " " + title_cap(lang) + "!";
}

function updateTitlePractise() {
    var lang=document.getElementById("lang_select").value;
    document.getElementById("title_practice").innerHTML=default_title + " " + title_cap(lang) + "!";
}
