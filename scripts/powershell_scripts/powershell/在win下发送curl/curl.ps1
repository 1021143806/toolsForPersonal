curl -H "Content-Type:application/json" -X POST -d '{"doorCode":"D001"}' http://10.68.2.31:9090/door/getStatus
curl -H "Content-Type:application/json" -X POST -d '{
"qrContent":"12345737",
"nodeStatus":"2"
}' http://10.68.2.31:7000/ics/stock/update/appStockStatus