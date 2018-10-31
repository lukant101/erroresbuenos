var default_title="Let's Practice";
var eavesdropped_audio = [];
// flag to keep track if load_question request is for a question in a new language
var changed_langauge = false;

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

// plays audio when user clicks the audio button
// also keep track of played audio for marking the question
function playAudioOut() {
    var audio_out=document.getElementById('card_audio');
    audio_out.play();
    var curr_lang = $("#lang_select").val();
    if (!(eavesdropped_audio.includes(curr_lang))) {
        eavesdropped_audio.push(curr_lang);
    }
}

// when user plays audio, disable answer input field and change colour of send button
$(document).ready(function() {
    $("#play_button").click( function() {
        $("#user_answer").prop("disabled",true);
        if ($("#send_answer_btn").hasClass("btn-info")) {
            $("#send_answer_btn").removeClass("btn-info");
            $("#send_answer_btn").addClass("btn-warning");
        }

    });
});

// ask for a new question when user changes language in dropdown menu
$(document).ready(function() {
    $("#lang_select").change( function() {
        changed_langauge = true;
        // enable / disable answer input depending if audio listened to for
        // the current question for this language
        if (eavesdropped_audio.includes($("#lang_select").val())) {
            $("#user_answer").prop("disabled",true);
            if ($("#send_answer_btn").hasClass("btn-info")) {
                $("#send_answer_btn").removeClass("btn-info");
                $("#send_answer_btn").addClass("btn-warning");
            }
        } else {
            $("#user_answer").prop("disabled",false);
            if ($("#send_answer_btn").hasClass("btn-warning")) {
                $("#send_answer_btn").removeClass("btn-warning");
                $("#send_answer_btn").addClass("btn-info");
            }
        }
        $.get("/next-question",
                {
                    language : $("#lang_select").val()
                },
                load_question, "json"
        );
    });
});

// sends user's answer and asks for a new question when user clicks the submit button
$(document).ready(function() {
    $("#send_answer_btn").click( function() {
        markAnswer();
        showAnswer();
    });
});

function markAnswer() {
    var user_answer = $("#user_answer").val().toLowerCase().trim();
    var answer = $("#answer").val().toLowerCase();
    var language = $("#lang_select").val();
    var part_of_speech = $("#part_of_speech_elem").text();
    console.log("User answer:");
    console.log(user_answer);
    console.log("Correct answer:");
    console.log(answer);
    console.log(part_of_speech);

    // answer is false be default, unless it passes in one of the tests
    var answer_correct="false";

    if (answer===user_answer) {
        answer_correct="true";
    }

    // try matching by ignoring "to" in english verbs
    if (answer_correct!="true" && language === "english" && part_of_speech === "verb") {
        console.log("english verbs clause")
        console.log(answer.slice(3));
        if (answer.slice(3)===user_answer) {
            answer_correct="true";
        }
    }

    // ignore articles in front of nouns
    if (answer_correct!="true" && part_of_speech === "noun" &&
        (language === "english" || language === "spanish")) {
        var start = user_answer.indexOf(" ");
        console.log("start:");
        console.log(start);
        if (start != -1) {
            var user_answer_mod = user_answer.slice(start+1);
            if (answer===user_answer_mod) {
                answer_correct="true";
            }
        }
    }

    // if correct answer has parentheses, ignore the brackets portion and compare
    if (answer_correct!="true" && answer.indexOf("\(") != -1) {
        console.log("word with parentheses");
        var end_user_answer = user_answer.indexOf("\(");
        if (end_user_answer === -1) {
            // user did not use parentheses, so leave answer unmodified
            user_answer_mod = user_answer;
        } else {
            var user_answer_mod = user_answer.slice(0, end_user_answer);
        }
        console.log("User answer trimmed:");
        console.log(user_answer_mod);
        var end_answer = answer.indexOf("\(");
        var answer_mod = answer.slice(0, end_answer);
        console.log("Correct answer trimmed:");
        console.log(answer_mod);
        if (answer_mod===user_answer_mod) {
            answer_correct="true";
        }
    }

    $("#answer_correct").val(answer_correct);
}

// event listener: the red "wrong" button is pressed to submit the answer
$(document).ready(function() {
    $("#wrong_answer_btn").click(function() {
        $("#wrong_answer_btn").fadeOut(function(){
            $("#send_answer_btn").fadeIn();});
        $("#show_answer").hide();
        $("#gtranslate").hide();
        submitAnswer();
    });
});

function showAnswer() {
    if ($("#answer_correct").val()==="true") {
        console.log("right answer");
        $("#good_job_msg").fadeIn().delay(800).fadeOut(submitAnswer);
    } else {
        console.log("wrong answer");
        $("#send_answer_btn").hide();
        // $("#wrong_answer_btn").click(submitAnswer);
        $("#wrong_answer_btn").fadeIn();
        $("#show_answer").fadeIn();
        $("#gtranslate").fadeIn();
    }
}



function submitAnswer() {
    // flag to keep track of if load_question request is for a question in a new language
    changed_langauge = false;
    $.post("/next-question",
            {
                user_answer : $("#user_answer").val().trim().toLowerCase(),
                question_id : $("#question_id").val(),
                student_id : $("#student_id").val(),
                answer_correct : $("#answer_correct").val(),
                audio_answer_correct : $("#audio_answer_correct").val(),
                language : $("#lang_select").val()
            },
            load_question, "json"
    );
}

// callbback function - loads a new question
function load_question(new_question)  {
    console.log(new_question);
    var quest_obj=new_question;
    $("#fcard").attr("src", "../static/pics/" + quest_obj.image_files.split(",")[0]);
    $("#audio_src").attr("src", "../static/audio/" + quest_obj.language.toLowerCase() + "/" + quest_obj.audio_files);
    // reload the audio source in the audio element; jQuery doesn't implement $().load(), so use JavaScript
    document.getElementById('card_audio').load();
    $("#part_of_speech_elem").text(quest_obj.part_of_speech);
    $("#word_elem").text(quest_obj.word);
    $("#user_answer").val("");
    $("#answer").val(quest_obj.word);
    $("#question_id").attr("value", quest_obj.id);

    if (changed_langauge===false) {
        // remove the current language from the eavesdropped_audio array
        // because the audio that student listened to is no longer in context
        current_language_index = eavesdropped_audio.indexOf($("#lang_select").val());
        if (current_language_index != -1) {
            eavesdropped_audio.splice(current_language_index,1);
            // enable the answer input for this language
            $("#user_answer").prop("disabled",false);
            // if necessary, change send button colour back to default
            if ($("#send_answer_btn").hasClass("btn-warning")) {
                $("#send_answer_btn").removeClass("btn-warning");
                $("#send_answer_btn").addClass("btn-info");
            }

        }

    }
}
