---
name: java-spring-boot-expert
description: "当用户创建或修改 Spring Boot 项目代码时使用此 skill,按团队约定的分层结构(Controller / Service / Repository)、统一异常处理(@ControllerAdvice + BusinessException)、日志规范(关键业务 INFO + 异常 ERROR + 脱敏)生成代码。支持 Spring Boot 2.x / 3.x,Java 11+。当用户提到「Spring Boot 规范」「Java 后端规范」「分层架构」「Controller 写哪里」「Spring Boot 编码风格」等关键词时使用。不适用于:(1) Spring Cloud 微服务治理(那是另一个 skill);(2) Spring MVC 老项目(用对应 skill);(3) 非 Spring Boot 的 Java 框架(如 Quarkus)。"
license: Apache 2.0
---

# Java Spring Boot Expert(Spring Boot 后端开发规范)

你是 **Spring Boot 后端开发规范专家**,让 AI 按团队约定的**分层结构 / 异常处理 / 日志规范**生成代码,而不是每次都从头设计。

## 核心能力

### 1. 分层结构
- Controller:只做参数校验 + 调 Service + 返回 DTO
- Service:业务逻辑,事务边界
- Repository / Mapper:数据库访问
- **禁止跨层调用**(Controller 不能直接调 Repository)
- DTO / VO / Entity 严格分离

### 2. 命名规范
- 类:PascalCase,如 `UserService`
- 方法:camelCase,如 `getUserById`
- 常量:全大写下划线,如 `MAX_RETRY_COUNT`
- 包:全小写,如 `com.example.user`

### 3. 异常处理
- 不吞异常
- 统一业务异常 `BusinessException`
- 全局 `@ControllerAdvice` 统一处理
- 错误响应格式统一 `{code, msg, data}`

### 4. 日志规范
- 关键业务入口 / 出口 INFO
- 异常 ERROR + 完整堆栈
- **不输出敏感信息**(身份证 / 密码 / token)
- 用 SLF4J + Lombok `@Slf4j`

### 5. 事务管理
- `@Transactional` 在 Service 层(不在 Controller)
- 只读事务 `@Transactional(readOnly = true)`
- 异常回滚 `rollbackFor = Exception.class`

## 关键规则

### 必须遵守
- ✅ 分层调用,Controller → Service → Repository
- ✅ 所有异常向上抛,统一处理
- ✅ 业务异常用 `BusinessException` 包装
- ✅ 关键操作记录 INFO 日志
- ✅ 异常记录 ERROR + stack trace
- ✅ 日志脱敏(身份证 / 卡号 / 手机号)
- ✅ 参数校验 `@Valid` + JSR-303 注解

### 禁止
- ❌ Controller 直接调 Repository
- ❌ 吞异常(`catch (Exception e) {}`)
- ❌ 在 Controller 写业务逻辑
- ❌ 日志打印密码 / token / 身份证
- ❌ 用 `System.out.println`(用 logger)
- ❌ 用 `Optional` 当参数类型

## 工作流程

### 第一步:扫描项目
```bash
ls src/main/java/com/example/
# 找包结构: controller / service / repository / dto / exception
cat pom.xml | grep -A 2 "<artifactId>"
```

### 第二步:确定架构
- Spring Boot 版本
- ORM(JPA / MyBatis / MyBatis-Plus)
- 数据库(MySQL / PostgreSQL)
- 缓存(Redis / Caffeine)
- 安全框架(Spring Security / Sa-Token)

### 第三步:生成代码模板

**Controller**:
```java
@RestController
@RequestMapping("/api/v1/users")
@RequiredArgsConstructor
@Slf4j
public class UserController {

    private final UserService userService;

    @GetMapping("/{id}")
    public Result<UserVO> getUser(@PathVariable Long id) {
        UserVO user = userService.getById(id);
        return Result.success(user);
    }

    @PostMapping
    public Result<UserVO> createUser(@Valid @RequestBody UserCreateDTO dto) {
        UserVO user = userService.create(dto);
        return Result.success(user);
    }
}
```

**Service**:
```java
@Service
@RequiredArgsConstructor
@Slf4j
public class UserServiceImpl implements UserService {

    private final UserRepository userRepository;

    @Override
    @Transactional(readOnly = true)
    public UserVO getById(Long id) {
        User user = userRepository.findById(id)
            .orElseThrow(() -> new BusinessException(ErrorCode.USER_NOT_FOUND));
        return UserConverter.toVO(user);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public UserVO create(UserCreateDTO dto) {
        log.info("Creating user: {}", dto.getUsername());
        User user = UserConverter.toEntity(dto);
        user = userRepository.save(user);
        return UserConverter.toVO(user);
    }
}
```

**Repository**:
```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByUsername(String username);
}
```

### 第四步:统一异常处理
```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(BusinessException.class)
    public Result<Void> handleBusiness(BusinessException e) {
        log.warn("业务异常: code={}, msg={}", e.getCode(), e.getMessage());
        return Result.fail(e.getCode(), e.getMessage());
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public Result<Void> handleValidation(MethodArgumentNotValidException e) {
        String msg = e.getBindingResult().getFieldErrors().stream()
            .map(FieldError::getDefaultMessage)
            .collect(Collectors.joining(","));
        return Result.fail(ErrorCode.PARAM_INVALID.getCode(), msg);
    }
}
```

## 使用示例

### 示例 1:写 CRUD 接口

```java
@RestController
@RequestMapping("/api/v1/products")
@RequiredArgsConstructor
public class ProductController {

    private final ProductService productService;

    @GetMapping("/{id}")
    public Result<ProductVO> get(@PathVariable Long id) {
        return Result.success(productService.getById(id));
    }

    @PostMapping
    public Result<ProductVO> create(@Valid @RequestBody ProductDTO dto) {
        return Result.success(productService.create(dto));
    }

    @PutMapping("/{id}")
    public Result<ProductVO> update(@PathVariable Long id, @Valid @RequestBody ProductDTO dto) {
        return Result.success(productService.update(id, dto));
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        productService.delete(id);
        return Result.success();
    }
}
```

### 示例 2:扫描现有项目

```bash
$ python scripts/spring_audit.py --path ./src/main/java
扫描中...
[🔴] UserController.java:42 — Controller 直接调 Repository
[🟡] OrderService.java:88 — 异常被吞
[🟢] ProductService.java — 全部合规
```

## 注意事项

### 常见误区
- ❌ `@Transactional` 加在 Controller → 事务边界应在 Service
- ❌ 用 `Optional` 当方法参数 → 反模式
- ❌ 异常吞掉后只 log 不抛 → 调用方不知道失败

### 关键警告
⚠️ `@Transactional` 不要用在 `private` 方法(代理失效)
⚠️ 循环依赖用 `@Lazy` 或重构(不要 `@Autowired` 注入自己)
⚠️ 生产环境**不要** `show-sql: true`(用 actuator 监控 SQL)
⚠️ 日志**不要**打印请求体含敏感字段(过滤中间件 + 注解)

## 参考资源
- [Spring Boot 官方文档](https://spring.io/projects/spring-boot)
- [阿里巴巴 Java 开发手册](https://github.com/alibaba/p3c)
- [Effective Java (Joshua Bloch)](https://www.oreilly.com/library/view/effective-java/9780134686091/)
- [MyBatis-Plus](https://baomidou.com/)