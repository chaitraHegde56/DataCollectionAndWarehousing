--- Create table category to save category details ---
CREATE TABLE `category`(
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(512) NOT NULL,
  `link` varchar(512) NOT NULL,
  PRIMARY KEY (`id`)
)ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


--- Create table books to save books details ---
CREATE TABLE `books` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(512) NOT NULL,
  `image_link` varchar(512) DEFAULT NULL,
  `rating` int(11) DEFAULT NULL,
  `price` decimal(4,2) DEFAULT NULL,
  `availability` int(11) NOT NULL,
  `category_id` int(11),
  `currency` varchar(512) DEFAULT 'POUNDS',
  `sys_created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `sys_updated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_category_id` (`category_id`),
  CONSTRAINT `fk_category_id` FOREIGN KEY (`category_id`) REFERENCES `category` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

