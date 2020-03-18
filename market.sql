CREATE TABLE `quotes` (
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `symbol` varchar(5) NOT NULL,
  `price` decimal(13,4) NOT NULL DEFAULT '0.0000',
  UNIQUE KEY `time_symbol_idx` (`time`,`symbol`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
