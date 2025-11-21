$uri = 'http://10.68.2.31:7000/ics/stock/update/appStockStatus'
 
$hash = @{qrContent = '12345737' ;
        nodeStatus = '2' ;
        }
$headers = @{"accept"="application/json" ;
        "Content-Type" = "application/json";
        }
$JSON = $hash | convertto-json
curl -h $header -uri $uri -Method POST -Body $JSON

