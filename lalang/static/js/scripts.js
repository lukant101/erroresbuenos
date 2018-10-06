// plays audio when user clicks the audio button
function playAudioOut() {
    var audio_out=document.getElementById('card_audio');
    audio_out.play();
}

// ask for a new question when user changes language in dropdown menu
$(document).ready(function() {
    $("#lang_select").change( function() {
        $.get("/next-question",
                {
                    language : $("#lang_select").val()
                },
                load_question
        );
    });
});

// sends user's answer and asks for a new question when user clicks the submit button
$(document).ready(function() {
    $("#send_answer_btn").click( function() {
        $.post("/next-question",
                {
                    user_answer : $("#user_answer").val(),
                    question_id : $("#question_id").val(),
                    student_id : $("#student_id").val(),
                    answer_correct : $("#answer_correct").val(),
                    audio_answer_correct : $("#audio_answer_correct").val(),
                    language : $("#lang_select").val()
                },
                load_question
        );
    });
});

// callbback function - loads a new question
function load_question(new_question)  {
    var quest_obj = JSON.parse(new_question);
    $("#fcard").attr("src", "../static/pics/" + quest_obj.image_files.split(",")[0]);
    $("#audio_src").attr("src", "../static/audio/" + quest_obj.language.toLowerCase() + "/" + quest_obj.audio_files);
    // reload the audio source in the audio element; jQuery doesn't implement $().load(), so use JavaScript
    document.getElementById('card_audio').load();
    $("#part_of_speech_elem").text(quest_obj.part_of_speech);
    $("#word_elem").text(quest_obj.word);
    $("#user_answer").val("");
    $("#question_id").attr("value", quest_obj.id);
}

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
