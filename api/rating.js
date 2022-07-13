$('#star_0').click(function(){
    $('#star_0').attr("src", "../../static/images/rating_fill.png");
    $('#star_1').attr("src", "../../static/images/rating.png");
    $('#star_2').attr("src", "../../static/images/rating.png");
    $('#star_3').attr("src", "../../static/images/rating.png");
    $('#star_4').attr("src", "../../static/images/rating.png");
    $('#ratings').attr("src","../../static/images/x_unhappy.png");
    $('#rating_content').attr('value','1');
});
$('#star_1').click(function(){
    $('#star_0').attr("src", "../../static/images/rating_fill.png");
    $('#star_1').attr("src", "../../static/images/rating_fill.png");
    $('#star_2').attr("src", "../../static/images/rating.png");
    $('#star_3').attr("src", "../../static/images/rating.png");
    $('#star_4').attr("src", "../../static/images/rating.png");
    $('#ratings').attr("src","../../static/images/unhappy.png");
    $('#rating_content').attr('value','2');
});
$('#star_2').click(function(){
    $('#star_0').attr("src", "../../static/images/rating_fill.png");
    $('#star_1').attr("src", "../../static/images/rating_fill.png");
    $('#star_2').attr("src", "../../static/images/rating_fill.png");
    $('#star_3').attr("src", "../../static/images/rating.png");
    $('#star_4').attr("src", "../../static/images/rating.png");
    $('#ratings').attr("src","../../static/images/ok.png");
    $('#rating_content').attr('value','3');
});
$('#star_3').click(function(){
    $('#star_0').attr("src", "../../static/images/rating_fill.png");
    $('#star_1').attr("src", "../../static/images/rating_fill.png");
    $('#star_2').attr("src", "../../static/images/rating_fill.png");
    $('#star_3').attr("src", "../../static/images/rating_fill.png");
    $('#star_4').attr("src", "../../static/images/rating.png");
    $('#ratings').attr("src","../../static/images/happy.png");
    $('#rating_content').attr('value','4');
});
$('#star_4').click(function(){
    $('#star_0').attr("src", "../../static/images/rating_fill.png");
    $('#star_1').attr("src", "../../static/images/rating_fill.png");
    $('#star_2').attr("src", "../../static/images/rating_fill.png");
    $('#star_3').attr("src", "../../static/images/rating_fill.png");
    $('#star_4').attr("src", "../../static/images/rating_fill.png");
    $('#ratings').attr("src","../../static/images/xtrahappy.png");
    $('#rating_content').attr('value','5');
});