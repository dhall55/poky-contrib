var progress_id = "loading";
function SetProgress(progress) {
  if (progress) {
      $("#" + progress_id + " > div").css("width", String(progress) + "%");
      $("#" + progress_id + " > div").html(String(progress) + "%");
  }
}