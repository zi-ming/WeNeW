

CREATE DATABASE IF NOT EXISTS wenew DEFAULT CHARSET utf8 COLLATE utf8_general_ci;


USE wenew;
ALTER TABLE Subpage_data MODIFY ctime DATETIME DEFAULT NOW();


USE wenew;
DELIMITER $$
DROP PROCEDURE IF EXISTS `queryNewList_proc` $$
CREATE PROCEDURE `queryNewList_proc`(
	IN _user_id INT,
	IN _latest_id INT,
	IN _type CHAR(10),
	IN _read_count INT
)
BEGIN
	DECLARE _is_superuser tinyint(1) default 0;
	IF _user_id != -1 THEN
		select is_superuser into _is_superuser from UserAction_user where id=_user_id limit 1;
		IF _is_superuser = 1 THEN		-- superuser
			IF _type = "getcount" THEN
					IF _latest_id = -1 THEN	select count(*) from Subpage_data;
					ELSE 	select count(*) from Subpage_data where id>_latest_id;
					END IF;		-- _latest_id
			ELSEIF _latest_id = -1 THEN
				select id,title,author,time,img1,brief from Subpage_data order by id desc limit _read_count;
			ELSEIF _type = "getnew" THEN
				select id,title,author,time,img1,brief from Subpage_data where id>_latest_id order by id limit _read_count;
			ELSE
				select id,title,author,time,img1,brief from Subpage_data where id<_latest_id order by id desc limit _read_count;
			END IF;

		ELSE	-- normal user
			IF _type = "getcount" THEN
					IF _latest_id = -1 THEN
						select count(*) from Subpage_data where xpath_id in(
							select id from Subpage_xpath where website_id in(
								select website_id from Subpage_user_sub where user_id=_user_id));
					ELSE
						select count(*) from Subpage_data where id>_latest_id and xpath_id in(
							select id from Subpage_xpath where website_id in(
								select website_id from Subpage_user_sub where user_id=_user_id));
					END IF;		-- _latest_id
			ELSEIF _latest_id = -1 THEN
				select id,title,author,time,img1,brief from Subpage_data where xpath_id in(
						select id from Subpage_xpath where website_id in(
							select website_id from Subpage_user_sub where user_id=_user_id)) order by id desc limit _read_count;
			ELSEIF _type = "getnew" THEN
				select id,title,author,time,img1,brief from Subpage_data where id>_latest_id and xpath_id in(
					select id from Subpage_xpath where website_id in(
						select website_id from Subpage_user_sub where user_id=_user_id)) order by id limit _read_count;
			ELSE
				select id,title,author,time,img1,brief from Subpage_data where id<_latest_id and xpath_id in(
							select id from Subpage_xpath where website_id in(
								select website_id from Subpage_user_sub where user_id=_user_id)) order by id desc limit _read_count;
			END IF;
		END IF;
	END IF;
END $$
DELIMITER ;




USE wenew;
DELIMITER $$
DROP PROCEDURE IF EXISTS `dataInsert_proc` $$
CREATE DEFINER=`root`@`127.0.0.1` PROCEDURE dataInsert_proc(
	in _title VARCHAR(100),
	in _author VARCHAR(100),
	in _time VARCHAR(100),
	in _content LONGTEXT,
	in _img1 VARCHAR(100),
	in _img2 VARCHAR(100),
	in _img3 VARCHAR(100),
	in _brief VARCHAR(1000),
	in _url VARCHAR(1000),
	in _xpath_id INT
)
BEGIN
	DECLARE _exit_count INT DEFAULT -1;
	select count(*) into _exit_count from Subpage_data where url=_url or title=_title;
	if _exit_count = 0 then
		insert into Subpage_data(url,title,author,time,content,img1,img2,img3,brief,xpath_id) 
		values(_url,_title,_author,_time,_content,_img1,_img2,_img3,_brief,_xpath_id);
	end if;
END $$
DELIMITER ;


USE wenew;
DELIMITER $$
DROP PROCEDURE IF EXISTS `queryWebsite_proc` $$
CREATE PROCEDURE `queryWebsite_proc`(
IN _user_id	INT
)
BEGIN
	DECLARE _flag INT DEFAULT 0;
	select is_superuser into _flag from UserAction_user where id = _user_id;
	IF _flag != 1 THEN
		select y.id, y.url, y.detail from Subpage_user_sub x inner join Subpage_website y on x.website_id = y.id
		where x.user_id=_user_id and y.is_activate = 1;
	ELSE
		select id, url, detail from Subpage_website;
	END IF;
END $$
DELIMITER ;


USE wenew;
DELIMITER $$
DROP PROCEDURE IF EXISTS `cancleWebsiteSub_proc` $$
CREATE PROCEDURE `cancleWebsiteSub_proc`(
IN _user_id	INT,
IN _website_id INT
)
BEGIN
	DECLARE _flag INT DEFAULT 0;
	select is_superuser into _flag from UserAction_user where id = _user_id;
	IF _flag != 1 THEN
		delete from Subpage_user_sub where user_id=_user_id and website_id = _website_id;
	ELSE
		delete from Subpage_data where xpath_id in (select id from Subpage_xpath where website_id=_website_id);
		delete from Subpage_xpath where website_id = _website_id;
		delete from Subpage_user_sub where website_id = _website_id;
		delete from Subpage_website_xpath where website_id = _website_id;
		delete from Subpage_website where id = _website_id;
	END IF;
END $$
DELIMITER ;


USE wenew;
ALTER TABLE Subpage_website_msg MODIFY ctime DATETIME DEFAULT NOW();

USE wenew;
DELIMITER $$
DROP PROCEDURE IF EXISTS `queryWebsiteMsg_proc` $$
CREATE PROCEDURE `queryWebsiteMsg_proc`(
	IN _website_id INT
)
BEGIN
	select y.url, x.content_url, x.msg from Subpage_website_msg x inner join Subpage_website y on x.website_id=y.id where x.website_id=_website_id;
END $$
DELIMITER ;



USE wenew;
DELIMITER $$
DROP PROCEDURE IF EXISTS `writeWebsiteMsg_proc` $$
CREATE PROCEDURE `writeWebsiteMsg_proc`(
	IN _website_id INT,
	IN _content_url VARCHAR(1000)
)
BEGIN
	DECLARE _flag INT default 0;
	select count(*) into _flag from Subpage_website_msg where website_id=_website_id and content_url=_content_url;
	IF _flag = 0 THEN
		insert into Subpage_website_msg(website_id, content_url) values(_website_id, _content_url);
	END IF ;
END $$
DELIMITER ;



USE wenew;
DELIMITER $$
DROP PROCEDURE IF EXISTS `clearLog_proc` $$
CREATE PROCEDURE `clearLog_proc`(
	IN _user_id INT
)
BEGIN
	DECLARE _flag INT default 0;
	select is_superuser into _flag from UserAction_user where id=_user_id;
	IF _flag = 1 THEN
		delete from Subpage_website_msg;
	ELSE
		delete from Subpage_website_msg where website_id in (select website_id from Subpage_user_sub where user_id=_user_id);
	END IF ;
END $$
DELIMITER ;



USE wenew;
DELIMITER $$
DROP PROCEDURE IF EXISTS `queryWebsiteMsg_proc` $$
CREATE PROCEDURE `queryWebsiteMsg_proc`(
	IN _user_id INT
)
BEGIN
	DECLARE _flag INT default 0;
	select is_superuser into _flag from UserAction_user where id=_user_id;
	IF _flag = 1 THEN
		select y.url, y.detail, x.content_url from Subpage_website_msg x
		inner join Subpage_website y on x.website_id=y.id;
	ELSE
		select y.url, y.detail, x.content_url from Subpage_website_msg x
		inner join (select a.id, a.url, a.detail from Subpage_website a
		inner join Subpage_user_sub b on a.id=b.website_id where b.user_id=_user_id) y on x.website_id=y.id;
	END IF ;
END $$
DELIMITER ;


USE wenew;

-- ----------------------------
-- Records of UserAction_user
-- ----------------------------
INSERT INTO `UserAction_user` VALUES ('1', 'pbkdf2_sha256$36000$KJLeFGOxSsN9$5AIM5OgkLCFzqNxBicE/j6qobU0ixc0JxrSZ+/J8iv0=', '2017-10-07 09:51:41.546668', '0', '123', null, '', '', '100', '2017-09-06 23:45:05.045421', '0');
INSERT INTO `UserAction_user` VALUES ('2', 'pbkdf2_sha256$36000$FC8Xnswy1V22$HslRF7rN7i8d/gSbvf3So8B0e3QvTB5+aKR6DEKmdN8=', '2017-09-27 16:01:52.502010', '1', 'ziming', '', '', '', '100', '2017-09-21 09:50:04.936372', '1');
INSERT INTO `UserAction_user` VALUES ('3', 'pbkdf2_sha256$36000$BX7liNzK5Gox$k+Ho1gk19w98Cm5tg1NrXan5RHWxHd2MEX0YN8JVXbs=', '2017-09-22 15:40:56.653898', '0', '456', null, '', '', '100', '2017-09-22 15:40:54.136754', '0');



-- ----------------------------
-- Records of Subpage_website
-- ----------------------------
INSERT INTO `Subpage_website` VALUES ('1', 'https://www.huxiu.com/', '', '2017-09-06 23:45:41.562601', '1', '3000');
INSERT INTO `Subpage_website` VALUES ('2', 'http://www.whosmall.com/?sort=7', '', '2017-09-07 00:59:19.903100', '1', '14140');
INSERT INTO `Subpage_website` VALUES ('3', 'https://www.cnblogs.com/pick/', '', '2017-09-08 22:36:23.891341', '1', '18020');
INSERT INTO `Subpage_website` VALUES ('4', 'http://www.cnbeta.com/', '', '2017-09-10 18:21:45.187416', '1', '7210');
INSERT INTO `Subpage_website` VALUES ('5', 'http://www.tmtpost.com/', '', '2017-09-10 18:30:25.270163', '1', '11720');
INSERT INTO `Subpage_website` VALUES ('6', 'http://www.iheima.com/', '', '2017-09-10 18:41:25.630933', '1', '13520');
INSERT INTO `Subpage_website` VALUES ('7', 'http://www.ittime.com.cn/', '', '2017-09-11 14:37:08.627333', '1', '3000');
INSERT INTO `Subpage_website` VALUES ('8', 'http://www.yinfans.com/topic/bluray-movie/movie', '', '2017-09-19 22:01:47.333032', '1', '6000');
INSERT INTO `Subpage_website` VALUES ('9', 'http://top.aiweibang.com/article/L8O7MsOmw6_CtsOg', 'python6359', '2017-09-26 18:53:36.510820', '0', '4500');
INSERT INTO `Subpage_website` VALUES ('10', 'http://top.aiweibang.com/article/L8O-McOgw6rCtcOj', 'ldbym01', '2017-09-27 18:59:38.849090', '0', '0');
INSERT INTO `Subpage_website` VALUES ('11', 'http://top.aiweibang.com/article/L8O_OcOtw6bCusOm', 'python_shequ', '2017-09-27 19:01:32.970617', '0', '0');
INSERT INTO `Subpage_website` VALUES ('12', 'http://top.aiweibang.com/article/KMO5OMOnw6fCtA~~', 'ylynwm6688', '2017-09-27 19:07:34.730309', '0', '0');



-- ----------------------------
-- Records of Subpage_user_sub
-- ----------------------------
INSERT INTO `Subpage_user_sub` VALUES ('1', '1', '2');
INSERT INTO `Subpage_user_sub` VALUES ('2', '1', '3');
INSERT INTO `Subpage_user_sub` VALUES ('3', '1', '4');
INSERT INTO `Subpage_user_sub` VALUES ('4', '1', '5');
INSERT INTO `Subpage_user_sub` VALUES ('5', '1', '6');
INSERT INTO `Subpage_user_sub` VALUES ('6', '1', '7');
INSERT INTO `Subpage_user_sub` VALUES ('7', '1', '8');
INSERT INTO `Subpage_user_sub` VALUES ('8', '1', '1');
INSERT INTO `Subpage_user_sub` VALUES ('9', '2', '2');
INSERT INTO `Subpage_user_sub` VALUES ('10', '2', '1');
INSERT INTO `Subpage_user_sub` VALUES ('11', '1', '9');
INSERT INTO `Subpage_user_sub` VALUES ('12', '1', '10');
INSERT INTO `Subpage_user_sub` VALUES ('13', '1', '11');
INSERT INTO `Subpage_user_sub` VALUES ('14', '1', '12');


-- ----------------------------
-- Records of Subpage_website_xpath
-- ----------------------------
INSERT INTO `Subpage_website_xpath` VALUES ('1', '//body/div/div/div/div/div/h2/a', '2017-09-06 23:45:41.686057', '1');
INSERT INTO `Subpage_website_xpath` VALUES ('2', '//body/section/div/div/article/header/h2/a', '2017-09-07 00:59:20.045423', '2');
INSERT INTO `Subpage_website_xpath` VALUES ('3', '//body/div/div/div/div/div/h3/a', '2017-09-08 22:36:24.000348', '3');
INSERT INTO `Subpage_website_xpath` VALUES ('4', '//body/div/div/div/div/div/div/dl/dt/a', '2017-09-10 18:21:45.448431', '4');
INSERT INTO `Subpage_website_xpath` VALUES ('5', '//body/div/div/section/div/div/div/ul/li/div/h3/a', '2017-09-10 18:30:25.313165', '5');
INSERT INTO `Subpage_website_xpath` VALUES ('6', '//body/div/div/div/div/div/div/article/div/div/a', '2017-09-10 18:41:25.839945', '6');
INSERT INTO `Subpage_website_xpath` VALUES ('7', '//body/div/div/div/div/ul/dl/dd/h2/a', '2017-09-11 14:37:08.673336', '7');
INSERT INTO `Subpage_website_xpath` VALUES ('8', '//body/div/div/ul/li/div/div/h2/a', '2017-09-19 22:01:47.386035', '8');
INSERT INTO `Subpage_website_xpath` VALUES ('9', '//body/section/div/div/div/div/div/div/div/a', '2017-09-26 18:53:36.750834', '9');
INSERT INTO `Subpage_website_xpath` VALUES ('10', '//body/section/div/div/div/div/div/div/div/a', '2017-09-27 18:59:38.892092', '10');
INSERT INTO `Subpage_website_xpath` VALUES ('11', '//body/section/div/div/div/div/div/div/div/a', '2017-09-27 19:01:33.142627', '11');
INSERT INTO `Subpage_website_xpath` VALUES ('12', '//body/section/div/div/div/div/div/div/div/a', '2017-09-27 19:09:03.511387', '12');


-- ----------------------------
-- Records of Subpage_xpath
-- ----------------------------
INSERT INTO `Subpage_xpath` VALUES ('1', '//body/div/div/div/div/div/h1/text()', '//body/div/div/div/div/div/div/span/a/text()', '//body/div[5]/div[1]/div[1]/div[2]/div[2]/div[1]/span[2]/text()', '//body/div/div/div/div/div/div/img|//body/div/div/div/div/div/div/p', '2017-09-06 23:46:12.702150', '1');
INSERT INTO `Subpage_xpath` VALUES ('2', '//body/div/section/div/div/header/h1/text()', '//body/div/section/div/div/header/div/span[2]/a[1]/text()', '//body/div/section/div/div/header/div/span[1]/text()', '//body/div/section/div/div/article/div/div/h4|//body/div/section/div/div/article/div/div/p', '2017-09-07 01:00:03.915843', '2');
INSERT INTO `Subpage_xpath` VALUES ('3', '//body/div/section/div/div/header/h1/text()', '//body/div/section/div/div/header/div/span[2]/a[1]/text()', '//body/div/section/div/div/header/div/span[1]/text()', '//body/div/section/div/div/article/p|//body/div/section/div/div/article/ul/li|//body/div/section/div/div/article/h2', '2017-09-07 19:05:05.738593', '2');
INSERT INTO `Subpage_xpath` VALUES ('4', '//body/div/div/div/div/div/div/div/h1/a/text()', '//body/div/div/div/h1/a/text()', '', '//body/div/div/div/div/div/div/div/div/div/p|//body/div/div/div/div/div/div/div/div/div/h1|//body/div/div/div/div/div/div/div/div/div/blockquote/p|//body/div/div/div/div/div/div/div/div/div/ul/li|//body/div/div/div/div/div/div/div/div/div/ol/li|//body/div/div/div/div/div/div/div/div/div/h2|//body/div/div/div/div/div/div/div/div/div/h3|//body/div/div/div/div/div/div/div/div/div/div/pre', '2017-09-09 23:09:56.056618', '3');
INSERT INTO `Subpage_xpath` VALUES ('5', '//body/div/div/div/div/div/div/div/h1/a/text()', '//body/div/div/div/h1/a/text()', '', '//body/div/div/div/div/div/div/div/div/div/p|//body/div/div/div/div/div/div/div/div/div/ul/li|//body/div/div/div/div/div/div/div/div/div/h2|//body/div/div/div/div/div/div/div/div/div/blockquote/p|//body/div/div/div/div/div/div/div/div/div/pre/code|//body/div/div/div/div/div/div/div/div/div/h3', '2017-09-09 23:50:22.813420', '3');
INSERT INTO `Subpage_xpath` VALUES ('6', '//body/div/div/div/div/div/div/div/h1/a/text()', '//body/div/div/div/h1/a/text()', '', '//body/div/div/div/div/div/div/div/div/div/p/b|//body/div/div/div/div/div/div/div/div/div/div/span|//body/div/div/div/div/div/div/div/div/div/div/h2|//body/div/div/div/div/div/div/div/div/div/div/div/pre|//body/div/div/div/div/div/div/div/div/div/div/strong/span', '2017-09-09 23:54:20.211999', '3');
INSERT INTO `Subpage_xpath` VALUES ('7', '//body/div/div/div/div/div/header/h1/text()', '//body/div/div/div/div/div/header/div/span[3]/a[1]/span[1]/text()', '//body/div/div/div/div/div/header/div/span[1]/text()', '//body/div/div/div/div/div/div/div/p', '2017-09-10 18:23:31.364489', '4');
INSERT INTO `Subpage_xpath` VALUES ('8', '//body/div/div/section/div/article/h1/text()', '//body/div/div/section/div/article/div/a/text()', '//body/div/div/section/div/article/div[2]/span[2]/text()', '//body/div/div/section/div/article/p|//body/div/div/section/div/article/div/p|//body/div/div/section/div/article/div/h2', '2017-09-10 18:32:28.835231', '5');
INSERT INTO `Subpage_xpath` VALUES ('9', '//body/div[2]/div[2]/div[1]/div[1]/text()', '', '//body/div/div/div/div/span/time/text()', '//body/div/div/div/div/p|//body/div/div/div/p', '2017-09-10 18:46:54.859764', '6');
INSERT INTO `Subpage_xpath` VALUES ('10', '//body/div/div/div/div/div/div/h2/a/text()', '//body/div/div/div/h1/a/text()', '', '//body/div/div/div/div/div/div/div/div/p|//body/div/div/div/div/div/div/div/div/div/pre|//body/div/div/div/div/div/div/div/div/pre/code|//body/div/div/div/div/div/div/div/div/ul/li|//body/div/div/div/div/div/div/div/div/h1', '2017-09-10 18:59:06.600617', '3');
INSERT INTO `Subpage_xpath` VALUES ('11', '//body/div/div/div/h2/text()', '', '', '//body/div/div/div/div/div/p|//body/div/div/div/div/div/h2/strong', '2017-09-10 19:07:40.481010', '3');
INSERT INTO `Subpage_xpath` VALUES ('12', '//body/div/div/div/div/div/h1/text()', '//body/div/div/div/div/div/div/span/a/text()', '//body/div[5]/div[1]/div[1]/div[2]/div[2]/div[1]/div[1]/span[1]/text()', '//body/div/div/div/div/div/div/img|//body/div/div/div/div/div/div/p|//body/div/div/div/div/div/div/blockquote/p', '2017-09-10 23:07:33.804261', '1');
INSERT INTO `Subpage_xpath` VALUES ('13', '//body/div/div/div/div/div/h1/text()', '//body/div/div/div/div/div/div/span/a/text()', '//body/div[5]/div[1]/div[1]/div[2]/div[2]/div[1]/div[1]/span[1]/text()', '//body/div/div/div/div/div/div/img|//body/div/div/div/div/div/div/p', '2017-09-11 11:24:55.381669', '1');
INSERT INTO `Subpage_xpath` VALUES ('14', '//body/div/div/div/div/h2/text()', '//body/div/div/div/div/div/a/text()', '//body/div[1]/div[1]/div[1]/div[1]/div[1]/span[2]/text()', '//body/div/div/div/div/p|//body/div/div/div/div/p', '2017-09-11 14:38:58.021590', '7');
INSERT INTO `Subpage_xpath` VALUES ('15', '//body/div/div/div/div/div/h1/text()', '//body/div/div/div/div/div/div/span/a/text()', '//body/div[6]/div[1]/div[1]/div[2]/div[2]/div[1]/div[1]/span[1]/text()', '//body/div/div/div/div/div/div/img|//body/div/div/div/div/div/div/p', '2017-09-13 12:41:51.556014', '1');
INSERT INTO `Subpage_xpath` VALUES ('16', '//body/div/div/div/h1/text()', '//body/div[4]/div[3]/div[1]/div[1]/span[1]/text()', '//body/div[4]/div[3]/div[1]/div[1]/span[3]/text()', '//body/div/div/div/div/div/p|//body/div/div/div/div/div/div', '2017-09-19 22:03:56.827439', '8');
INSERT INTO `Subpage_xpath` VALUES ('17', '//body/div/div/div/div/div/h1/text()', '', '', '//body/div/div/div/div/div/div/img|//body/div/div/div/div/div/div/p', '2017-09-20 19:04:55.921981', '1');
INSERT INTO `Subpage_xpath` VALUES ('18', '//body/div/section/div/div/header/h1/text()', '//body/div/section/div/div/header/div/span[2]/a[1]/text()', '//body/div/section/div/div/header/div/span[1]/text()', '//body/div/section/div/div/article/div/div/p|//body/div/section/div/div/article/div/div/h2|//body/div/section/div/div/article/div/div/div/img', '2017-09-21 10:45:51.230769', '2');
INSERT INTO `Subpage_xpath` VALUES ('19', '//body/div[1]/div[2]/div[1]/div[1]/text()', '//body/div/div/div/div/a/span[2]/text()', '//body/div/div/div/div/span/time/text()', '//body/div/div/div/p', '2017-09-22 14:33:18.135764', '6');
INSERT INTO `Subpage_xpath` VALUES ('20', '//body/div/div/h1/a/text()', '', '', '//body/div/div/div/div/div/p', '2017-09-22 14:36:32.360873', '3');
INSERT INTO `Subpage_xpath` VALUES ('21', '//body/div/div/div/div/div/div/div/h1/a/text()', '', '', '//body/div/div/div/div/div/div/div/div/div', '2017-09-22 14:45:02.696063', '3');
INSERT INTO `Subpage_xpath` VALUES ('22', '//body/div/h1/a/text()', '', '', '//body/div/div/div/div/div/div', '2017-09-22 14:45:33.280812', '3');
INSERT INTO `Subpage_xpath` VALUES ('23', '//body/div/div/div/div/h2/text()', '//body/div[1]/div[2]/div[1]/div[1]/div[1]/em[2]/text()', '//body/div[1]/div[2]/div[1]/div[1]/div[1]/em[1]/text()', '//body/div/div/div/div/div/p', '2017-09-26 18:54:10.226748', '9');
INSERT INTO `Subpage_xpath` VALUES ('24', '//body/div/div/div/div/h2/text()', '//body/div[1]/div[2]/div[1]/div[1]/div[1]/em[2]/text()', '//body/div[1]/div[2]/div[1]/div[1]/div[1]/em[1]/text()', '//body/div/div/div/div/div/p/img', '2017-09-27 18:43:46.866640', '9');
INSERT INTO `Subpage_xpath` VALUES ('25', '//body/div/div/div/div/h2/text()', '//body/div[1]/div[2]/div[1]/div[1]/div[1]/em[2]/text()', '//body/div[1]/div[2]/div[1]/div[1]/div[1]/em[1]/text()', '//body/div/div/div/div/div/section/section/section/section/section/section/section|//body/div/div/div/div/div/section/section/section/section/p|//body/div/div/div/div/div/section/section/section/section/section/section/img', '2017-09-27 19:00:27.453870', '10');
INSERT INTO `Subpage_xpath` VALUES ('26', '//body/div/div/div/div/h2/text()', '//body/div[1]/div[2]/div[1]/div[1]/div[1]/em[2]/text()', '//body/div[1]/div[2]/div[1]/div[1]/div[1]/em[1]/text()', '//body/div/div/div/div/div/section/section/section/section/section/section/section|//body/div/div/div/div/div/section/section/section/section/p|//body/div/div/div/div/div/section/section/section/section/section/section/img', '2017-09-27 19:00:30.141024', '10');


/*
USE wenew;
DELIMITER $$
DROP PROCEDURE IF EXISTS `u_id` $$
CREATE PROCEDURE `u_id`()
BEGIN
	DECLARE _num INT DEFAULT 0;
	DECLARE _index INT;
	DECLARE _flag INT;
	DECLARE _id INT;
	
	set _index=1;
	select count(*) into _num from Subpage_website;

	SET FOREIGN_KEY_CHECKS=0;
	WHILE _index<=_num do
		SELECT id into _flag from Subpage_website where id>=_index order by id limit 1;
		UPDATE Subpage_website set id=_index where id=_flag;
		UPDATE Subpage_user_sub set website_id=_index where website_id=_flag;
		UPDATE Subpage_website_xpath set website_id=_index where website_id=_flag;
		UPDATE Subpage_xpath set website_id=_index where website_id=_flag;
		set _index = _index + 1;
	END WHILE;
	SET FOREIGN_KEY_CHECKS=1;
END $$
DELIMITER ;
call u_id();
DROP PROCEDURE IF EXISTS `u_id`;




USE wenew;
DELIMITER $$
DROP PROCEDURE IF EXISTS `u_id` $$
CREATE PROCEDURE `u_id`()
BEGIN
	DECLARE _num INT DEFAULT 0;
	DECLARE _index INT;
	DECLARE _flag INT;
	DECLARE _id INT;
	
	set _index=1;
	select count(*) into _num from Subpage_user_sub;

	SET FOREIGN_KEY_CHECKS=0;
	WHILE _index<=_num do
		SELECT id into _flag from Subpage_user_sub where id>=_index order by id limit 1;
		UPDATE Subpage_user_sub set id=_index where id=_flag;
		set _index = _index + 1;
	END WHILE;
	SET FOREIGN_KEY_CHECKS=1;
END $$
DELIMITER ;
call u_id();
DROP PROCEDURE IF EXISTS `u_id`;




USE wenew;
DELIMITER $$
DROP PROCEDURE IF EXISTS `u_id` $$
CREATE PROCEDURE `u_id`()
BEGIN
	DECLARE _num INT DEFAULT 0;
	DECLARE _index INT;
	DECLARE _flag INT;
	DECLARE _id INT;
	
	set _index=1;
	select count(*) into _num from Subpage_xpath;

	SET FOREIGN_KEY_CHECKS=0;
	WHILE _index<=_num do
		SELECT id into _flag from Subpage_xpath where id>=_index order by id limit 1;
		UPDATE Subpage_xpath set id=_index where id=_flag;
		set _index = _index + 1;
	END WHILE;
	SET FOREIGN_KEY_CHECKS=1;
END $$
DELIMITER ;
call u_id();
DROP PROCEDURE IF EXISTS `u_id`;
*/
