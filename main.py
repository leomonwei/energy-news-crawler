# main.py
"""
能源行业新闻爬虫 - 主入口
支持政策新闻 (zc) 和技术新闻 (js) 两种模式
版本：2.0
"""
import sys
import os
import argparse
import traceback
import json
from datetime import datetime, timedelta
from crawler import Crawler
from utils.parse_date import parse_date

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 动态导入蜘蛛类
def import_spiders():
    """动态导入所有蜘蛛类"""
    try:
        from spiders.bjx_spider import BjxUsualSpider
        from spiders.cpnn_spider import CpnnSpider
        from spiders.cnes_spider import CNESSpider
        from spiders.csg_spider import CsgSpider
        from spiders.cec_spider import CECSpider
        from spiders.gkzhan_spider import GkzhanSpider
        from spiders.nes_spider import NewEnergySpider
        from spiders.hydroe_spider import HydrogenEnergySpider
        from spiders.inen_spider import InEnSpider
        from spiders.escn_spider import ESCNSpider
        from spiders.nsa_spider import NsaSpider
        from spiders.scinet_spider import ScienceNetSpider
        from spiders.ccnta_spider import CcntaSpider
        from spiders.wechat_spider import WeChatSpider
        return True
    except ImportError as e:
        print(f"❌ 导入蜘蛛类失败：{e}")
        return False

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='能源行业新闻爬虫 v2.0',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py zc                    # 抓取政策新闻（最近 30 天，5 页）
  python main.py js --time_limit 7     # 抓取技术新闻（最近 7 天）
  python main.py solo --url "..."      # 抓取单个网站
  python main.py zc --max_pages 10     # 抓取更多页数
        """
    )
    
    # 运行模式参数
    parser.add_argument('mode', choices=['zc', 'js', 'solo', 'wechat'], 
                       help='运行模式：zc-政策新闻，js-技术新闻，solo-单个网站，wechat-微信公众号')
    
    # solo 模式专用参数
    parser.add_argument('--url', type=str, 
                       help='solo 模式下的网站 URL（仅当 mode=solo 时使用）')
    
    # 可选参数
    parser.add_argument('--time_limit', type=int, default=30,
                       help='时间过滤器（天数），默认 30 天，0 表示不过滤')
    parser.add_argument('--output_dir', type=str, default='./output',
                       help='输出目录，默认 ./output')
    parser.add_argument('--max_pages', type=int, default=5,
                       help='最大抓取页数，默认 5 页')
    parser.add_argument('--timeout', type=int, default=30,
                       help='请求超时时间（秒），默认 30 秒')
    parser.add_argument('--retry', type=int, default=3,
                       help='重试次数，默认 3 次')
    parser.add_argument('--workers', type=int, default=3,
                       help='并发线程数，默认 3')
    parser.add_argument('--debug', action='store_true',
                       help='启用调试模式，输出详细日志')
    parser.add_argument('--analyze', action='store_true',
                       help='使用Qwen大模型分析文章价值并筛选')
    parser.add_argument('--api_key', type=str,
                       help='阿里云DashScope API密钥（用于Qwen大模型分析）')
    parser.add_argument('--threshold', type=int, default=5,
                       help='文章价值筛选阈值，高于此分数的文章会被保留，默认 5')
    
    args = parser.parse_args()
    
    # 验证 solo 模式必须提供 url 参数
    if args.mode == 'solo' and not args.url:
        parser.error("❌ solo 模式必须提供 --url 参数")
    
    return args

def register_technical_spiders(crawler):
    """注册技术新闻爬虫"""
    spiders_config = [
        # 核心能源网站
        ('bjx_js', '北极星电力网 - 技术', 'https://news.bjx.com.cn/js/'),
        ('cpnn_dianli', '中国能源新闻网 - 电力', 'https://cpnn.com.cn/news/dianli2023/'),
        ('cpnn_kj', '中国能源新闻网 - 科技', 'https://cpnn.com.cn/news/kj/'),
        ('cnes_js', '储能中国网 - 技术', 'http://www.cnnes.cc/jishu/'),
        ('escn_js', '中国储能网 - 技术', 'https://www.escn.com.cn/news/599-1.html'),
        
        # 行业网站
        ('cec', '中国电力企业联合会', 'https://www.cec.org.cn/'),
        ('csg', '南方电网能源观察', 'https://www.csg.cn/xwzx/nygc/'),
        ('inen_js', '国际电力网 - 技术', 'https://power.in-en.com/tech/'),
        ('newe_js', '新能源网 - 技术', 'http://www.china-nengyuan.com/tech/tech_list_10.html'),
        ('hydro_js', '全球氢能网', 'http://h2.china-nengyuan.com/tech/'),
        ('gkzhan_js', '智能制造网 - 技术', 'https://www.gkzhan.com/news/t13/list.html'),
        
        # 政府/科研机构
        ('nsa_js', '国家核安全局', 'https://nnsa.mee.gov.cn/ztzl/haqshmhsh/haqrdmyyt/'),
        ('scinet_xxkx', '科学网 - 信息科学', 'https://news.sciencenet.cn/fieldlist.aspx?id=9'),
        ('scinet_gccl', '科学网 - 工程', 'https://news.sciencenet.cn/fieldlist.aspx?id=8'),
        ('ccnta_jszb', '中国核技术网 - 技术装备', 'https://www.ccnta.cn/channel/jishuzhuangbei.html'),
        ('ccnta_cyyy', '中国核技术网 - 产业应用', 'https://www.ccnta.cn/channel/chanyeyingyong.html'),
    ]
    
    # 动态导入
    from spiders.bjx_spider import BjxUsualSpider
    from spiders.cpnn_spider import CpnnSpider
    from spiders.cnes_spider import CNESSpider
    from spiders.escn_spider import ESCNSpider
    from spiders.cec_spider import CECSpider
    from spiders.csg_spider import CsgSpider
    from spiders.inen_spider import InEnSpider
    from spiders.nes_spider import NewEnergySpider
    from spiders.hydroe_spider import HydrogenEnergySpider
    from spiders.gkzhan_spider import GkzhanSpider
    from spiders.nsa_spider import NsaSpider
    from spiders.scinet_spider import ScienceNetSpider
    from spiders.ccnta_spider import CcntaSpider
    
    spider_map = {
        'bjx_js': BjxUsualSpider,
        'cpnn_dianli': CpnnSpider,
        'cpnn_kj': CpnnSpider,
        'cnes_js': CNESSpider,
        'escn_js': ESCNSpider,
        'cec': CECSpider,
        'csg': CsgSpider,
        'inen_js': InEnSpider,
        'newe_js': NewEnergySpider,
        'hydro_js': HydrogenEnergySpider,
        'gkzhan_js': GkzhanSpider,
        'nsa_js': NsaSpider,
        'scinet_xxkx': ScienceNetSpider,
        'scinet_gccl': ScienceNetSpider,
        'ccnta_jszb': CcntaSpider,
        'ccnta_cyyy': CcntaSpider,
    }
    
    registered = []
    for name, desc, url in spiders_config:
        try:
            spider_class = spider_map.get(name)
            if spider_class:
                crawler.add_spider(name, spider_class(url))
                registered.append(name)
                print(f"  ✓ {desc}")
        except Exception as e:
            print(f"  ✗ {desc}: {e}")
    
    return registered

def register_policy_spiders(crawler):
    """注册政策新闻爬虫"""
    spiders_config = [
        # 核心能源网站
        ('bjx_zc', '北极星电力网 - 政策', 'https://news.bjx.com.cn/zc/'),
        ('cpnn_zc', '中国能源新闻网 - 地方能源', 'https://cpnn.com.cn/news/dfny/'),
        ('cnes_zc', '储能中国网 - 政策', 'http://www.cnnes.cc/zhengce/'),
        ('escn_zc', '中国储能网 - 政策', 'https://www.escn.com.cn/news/564.html'),
        
        # 行业网站
        ('inen_zc', '国际电力网 - 政策', 'https://power.in-en.com/policy/'),
        ('newe_zc', '新能源网 - 政策', 'http://www.china-nengyuan.com/news/news_list_6.html'),
        ('gkzhan_zc', '智能制造网 - 政策', 'https://www.gkzhan.com/news/t11/list.html'),
        
        # 政府/科研机构
        ('ccnta_zc', '中国核技术网 - 政策法规', 'https://www.ccnta.cn/channel/zhengcefagui.html'),
    ]
    
    # 动态导入
    from spiders.bjx_spider import BjxUsualSpider
    from spiders.cpnn_spider import CpnnSpider
    from spiders.cnes_spider import CNESSpider
    from spiders.escn_spider import ESCNSpider
    from spiders.inen_spider import InEnSpider
    from spiders.nes_spider import NewEnergySpider
    from spiders.gkzhan_spider import GkzhanSpider
    from spiders.ccnta_spider import CcntaSpider
    
    spider_map = {
        'bjx_zc': BjxUsualSpider,
        'cpnn_zc': CpnnSpider,
        'cnes_zc': CNESSpider,
        'escn_zc': ESCNSpider,
        'inen_zc': InEnSpider,
        'newe_zc': NewEnergySpider,
        'gkzhan_zc': GkzhanSpider,
        'ccnta_zc': CcntaSpider,
    }
    
    registered = []
    for name, desc, url in spiders_config:
        try:
            spider_class = spider_map.get(name)
            if spider_class:
                crawler.add_spider(name, spider_class(url))
                registered.append(name)
                print(f"  ✓ {desc}")
        except Exception as e:
            print(f"  ✗ {desc}: {e}")
    
    return registered

def run_crawler(crawler, spider_names, max_pages, time_limit, output_dir, debug=False):
    """运行爬虫并处理结果"""
    print(f"\n📡 开始抓取，共 {len(spider_names)} 个网站，最多 {max_pages} 页/站...")
    print("-" * 60)
    
    # 并发抓取
    all_results = crawler.run_multi(
        spider_names=spider_names,
        max_pages=max_pages,
        debug=debug
    )
    
    # 收集结果
    articles_list = []
    success_count = 0
    total_count = 0
    
    print("\n📊 抓取结果统计:")
    print("-" * 60)
    
    for site, articles in sorted(all_results.items(), key=lambda x: len(x[1]), reverse=True):
        total_count += len(articles)
        articles_list.extend(articles)
        status = "✓" if len(articles) > 0 else "✗"
        if len(articles) > 0:
            success_count += 1
        print(f"  {status} {site}: {len(articles)} 篇")
        if debug and articles:
            for art in articles[:2]:
                print(f"      - [{art.get('date')}] {art.get('title', '')[:50]}...")
    
    print("-" * 60)
    print(f"成功网站：{success_count}/{len(spider_names)}")
    print(f"总文章数：{total_count} 篇")
    
    # 时间过滤
    if time_limit > 0:
        current_time = datetime.now()
        time_limit_ago = current_time - timedelta(days=time_limit)
        filtered_articles = [
            art for art in articles_list 
            if parse_date(art.get('date')) and parse_date(art.get('date')) >= time_limit_ago
        ]
        print(f"\n⏰ 时间过滤：{total_count} → {len(filtered_articles)} 篇（最近{time_limit}天）")
        articles_list = filtered_articles
    else:
        print(f"\n⏰ 时间过滤：已禁用，保留所有 {len(articles_list)} 篇")
    
    # 文章去重
    unique_articles = {}
    duplicates = 0
    for art in articles_list:
        title = art.get('title', '').strip()
        if title and title not in unique_articles:
            unique_articles[title] = art
        else:
            duplicates += 1
    
    articles_list = list(unique_articles.values())
    print(f"🔄 去重处理：移除 {duplicates} 篇重复，剩余 {len(articles_list)} 篇")
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成输出文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(output_dir, f'articles_{timestamp}.csv')
    
    # 存储到 CSV（UTF-8-sig 编码，兼容 Excel）
    crawler.save_data(
        articles_list, 
        'csv',
        file_path=output_file,
        encoding='utf-8-sig'
    )
    
    print(f"\n✅ 保存完成：{output_file}")
    print(f"📁 共保存 {len(articles_list)} 篇文章")
    
    return articles_list

def main():
    """主函数"""
    print("=" * 60)
    print("       能源行业新闻爬虫 v2.0")
    print("=" * 60)
    
    # 解析命令行参数
    args = parse_arguments()
    
    print(f"\n📋 配置信息:")
    print(f"  运行模式：{args.mode}")
    print(f"  时间范围：最近 {args.time_limit} 天" if args.time_limit > 0 else "  时间范围：全部")
    print(f"  输出目录：{args.output_dir}")
    print(f"  最大页数：{args.max_pages}")
    print(f"  并发线程：{args.workers}")
    print(f"  调试模式：{'开启' if args.debug else '关闭'}")
    
    # 初始化爬虫
    crawler = Crawler(max_workers=args.workers, timeout=args.timeout, retry=args.retry)
    
    # 注册爬虫
    print(f"\n🕷️  注册爬虫:")
    if args.mode == 'js':
        print("  技术新闻模式:")
        spider_names = register_technical_spiders(crawler)
    elif args.mode == 'zc':
        print("  政策新闻模式:")
        spider_names = register_policy_spiders(crawler)
    elif args.mode == 'solo':
        from spiders.cpnn_spider import CpnnSpider
        crawler.add_spider('solo', CpnnSpider(args.url))
        spider_names = ['solo']
        print(f"  ✓ 单站模式：{args.url}")
    elif args.mode == 'wechat':
        print("  微信公众号模式:")
        from spiders.wechat_spider import WeChatSpider
        
        # 加载微信公众号ID列表
        wechat_file = os.path.join(os.path.dirname(__file__), 'wechat_official_account.json')
        try:
            with open(wechat_file, 'r', encoding='utf-8') as f:
                wechat_data = json.load(f)
            accounts = wechat_data.get('accounts', [])
            
            if not accounts:
                print("  ✗ 未找到公众号列表")
                spider_names = []
            else:
                # 微信API地址
                api_url = "https://down.mptext.top/api/public/v1/article"
                # 这里需要用户提供auth-key
                auth_key = input("  请输入微信API的auth-key: ")
                
                spider_names = []
                for account in accounts:
                    fakeid = account.get('fakeid')
                    nickname = account.get('nickname')
                    if fakeid and nickname:
                        try:
                            crawler.add_spider(
                                f'wechat_{nickname}', 
                                WeChatSpider(api_url, fakeid, auth_key, nickname)
                            )
                            spider_names.append(f'wechat_{nickname}')
                            print(f"  ✓ {nickname}")
                        except Exception as e:
                            print(f"  ✗ {nickname}: {e}")
        except Exception as e:
            print(f"  ✗ 加载公众号列表失败: {e}")
            spider_names = []
    
    if not spider_names:
        print("\n❌ 没有可用的爬虫，退出")
        return
    
    try:
        # 运行爬虫
        articles = run_crawler(
            crawler=crawler,
            spider_names=spider_names,
            max_pages=args.max_pages,
            time_limit=args.time_limit,
            output_dir=args.output_dir,
            debug=args.debug
        )
        
        # 使用Qwen大模型分析文章价值并筛选
        if args.analyze:
            if not args.api_key:
                print("\n⚠️  启用分析功能需要提供 --api_key 参数")
            else:
                print("\n🤖 开始使用Qwen大模型分析文章价值...")
                # 导入Qwen分析器
                from utils.qwen_analyzer import NewsAnalyzer, read_articles_csv, write_analyzed_articles_csv
                
                # 读取保存的CSV文件
                import glob
                import os
                csv_files = glob.glob(os.path.join(args.output_dir, 'articles_*.csv'))
                if csv_files:
                    # 获取最新的CSV文件
                    latest_csv = max(csv_files, key=os.path.getmtime)
                    print(f"正在分析文件: {latest_csv}")
                    
                    # 读取文章数据
                    articles_list = read_articles_csv(latest_csv)
                    if articles_list:
                        # 初始化分析器
                        analyzer = NewsAnalyzer(args.api_key, batch_size=5, threshold=args.threshold)
                        
                        # 分析文章
                        analyzed_articles = analyzer.analyze_batch_articles(articles_list)
                        
                        # 筛选文章
                        filtered_articles, removed_articles = analyzer.filter_articles(analyzed_articles)
                        
                        # 生成分析结果文件名
                        import datetime
                        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                        analyzed_output = os.path.join(args.output_dir, f'analyzed_articles_{timestamp}.csv')
                        
                        # 保存分析结果
                        write_analyzed_articles_csv(analyzed_output, filtered_articles)
                        
                        # 如果有移除的文章，也保存下来
                        if removed_articles:
                            removed_output = analyzed_output.replace('.csv', '_removed.csv')
                            write_analyzed_articles_csv(removed_output, removed_articles)
                            print(f"移除的文章已保存到 {removed_output}")
                    else:
                        print("未读取到有效的文章数据，分析失败")
                else:
                    print("未找到可分析的CSV文件")
        
        if not articles:
            print("\n⚠️  未抓取到任何文章，请检查网络连接或网站状态")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断，正在保存已抓取的数据...")
    except Exception as e:
        print(f"\n❌ 抓取过程出错：{e}")
        if args.debug:
            traceback.print_exc()
    finally:
        # 关闭线程池
        crawler.shutdown()
        print("\n👋 爬虫已关闭")

if __name__ == "__main__":
    main()
