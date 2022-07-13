function starBars(five_stars, four_stars, three_stars, two_stars, one_star,total_votes){
    var content_5_width = (five_stars/total_votes)*100+'%';
	var content_4_width = (four_stars/total_votes)*100+'%';
	var content_3_width = (three_stars/total_votes)*100+'%';
	var content_2_width = (two_stars/total_votes)*100+'%';
	var content_1_width = (one_star/total_votes)*100+'%';

    document.querySelector('.content_5_star_inner').style.width = content_5_width;
	document.querySelector('.content_4_star_inner').style.width = content_4_width;
	document.querySelector('.content_3_star_inner').style.width = content_3_width;
	document.querySelector('.content_2_star_inner').style.width = content_2_width;
	document.querySelector('.content_1_star_inner').style.width = content_1_width;
}