--
-- Create model Stock
--
CREATE TABLE `stock_stock` (`ts_code` varchar(9) NOT NULL PRIMARY KEY, `symbol` varchar(6) NOT NULL, `name` va
rchar(20) NOT NULL, `area` varchar(20) NOT NULL, `industry` varchar(20) NOT NULL, `list_date` datetime(6) NOT
NULL);
--
-- Create model Share
--
CREATE TABLE `stock_share` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `end_date` datetime(6) NOT NULL,
 `ann_date` datetime(6) NOT NULL, `div_proc` varchar(20) NOT NULL, `stk_div` double precision NOT NULL, `stk_b
o_rate` double precision NOT NULL, `stk_co_rate` double precision NOT NULL, `cash_div` double precision NOT NU
LL, `cash_div_tax` double precision NOT NULL, `record_date` datetime(6) NOT NULL, `ex_date` datetime(6) NOT NU
LL, `pay_date` datetime(6) NOT NULL, `div_listdate` datetime(6) NOT NULL, `imp_ann_date` datetime(6) NOT NULL,
 `base_date` datetime(6) NOT NULL, `base_share` double precision NOT NULL, `ts_code_id` varchar(9) NOT NULL);
ALTER TABLE `stock_share` ADD CONSTRAINT `stock_share_ts_code_id_548e7c30_fk_stock_stock_ts_code` FOREIGN KEY
(`ts_code_id`) REFERENCES `stock_stock` (`ts_code`);
