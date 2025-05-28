#from lxml.parser import filename
from playwright.sync_api import sync_playwright
import time
import random


class DynamicPageCrawler:
    def __init__(self):
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        ]

        # 代理配置（如果需要）
        self.proxy = None  # 示例：{'server': 'http://user:pass@host:port'}

    def get_full_html(self, url):
        with sync_playwright() as p:
            # 配置浏览器参数
            browser = p.chromium.launch(
                headless=True,  # 无头模式
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-infobars',
                    '--no-sandbox',
                    f'--user-agent={random.choice(self.user_agents)}'
                ]
            )

            context = browser.new_context(
                java_script_enabled=True,
                ignore_https_errors=True,
                proxy=self.proxy  # 配置代理
            )

            # 防止自动化检测
            context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
                window.chrome = {
                    runtime: {},
                };
            """)

            page = context.new_page()

            try:
                # 模拟真实用户访问模式
                page.goto(url, timeout=60000)

                # 滚动页面触发动态加载
                self._simulate_scroll(page)

                # 等待核心内容加载（根据目标网站调整）
                page.wait_for_selector('.vc_article', timeout=15000)
                page.wait_for_load_state('networkidle', timeout=15000)

                # 获取完整HTML
                html = page.content()

                return html
            except Exception as e:
                print(f"抓取失败: {str(e)}")
                return None
            finally:
                context.close()
                browser.close()

    def _simulate_scroll(self, page):
        """模拟人类滚动行为"""
        scroll_steps = random.randint(3, 6)
        for _ in range(scroll_steps):
            # 随机滚动距离
            scroll_height = random.randint(300, 800)
            page.evaluate(f"window.scrollBy(0, {scroll_height})")
            # 随机停留时间
            time.sleep(random.uniform(0.5, 2.5))

    def save_html(self, html,n):
        filename=".\\page_html\\note%d.html"%n
        with open(filename,"w",encoding="utf-8") as f:
            f.write(html)
        #print(f"完整页面已保存到 {filename}"


if __name__ == "__main__":
    crawler = DynamicPageCrawler()
    target_url = "https://www.mafengwo.cn/i/24643699.html"

    # 可选代理设置
    # crawler.proxy = {'server': 'http://your_proxy:port'}

    html_content = crawler.get_full_html(target_url)

    if html_content:
        print("成功获取完整页面内容！")
        crawler.save_html(html_content,96)

        # 验证内容完整性
        if 'vc_article' in html_content:
            print("检测到游记正文内容")
        else:
            print("警告：可能未完全加载，尝试以下解决方案：")
            print("1. 增加等待时间")
            print("2. 调整CSS选择器")
            print("3. 检查反爬机制")
    else:
        print("获取失败，建议：")
        print("1. 检查网络连接")
        print("2. 尝试更换User-Agent")
        print("3. 使用有效代理服务器")
