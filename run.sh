docker run -v $(pwd)/volumes:/var/volumes -v $(pwd)/post_list.json:/app/post_list.json fb_posts /var/volumes /app/post_list.json                                                                  
docker build -t fb_posts .

sudo docker run -v ~/test/volumes:/var/volumes --entrypoint python fb_posts scraper.py /var/volumes <fb_post_url>
# ex: sudo docker run -v ~/test/volumes:/var/volumes --entrypoint python fb_posts scraper.py /var/volumes "https://www.facebook.com/iamthatprophet/videos/2530938387225313"
