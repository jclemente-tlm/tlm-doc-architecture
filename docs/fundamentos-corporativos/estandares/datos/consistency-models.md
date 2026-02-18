---
id: consistency-models
sidebar_position: 1
title: Consistency Models
description: Modelos de consistencia para datos distribuidos - strong vs eventual consistency
---

# Consistency Models

## Contexto

Este estándar define **Consistency Models**: garantías sobre cuándo los cambios en datos distribuidos son **visibles** a todos los clientes. En sistemas distribuidos, replicación y particiones generan trade-offs entre **consistencia, disponibilidad y latencia** (CAP Theorem). Complementa el [lineamiento de Consistencia Eventual](../../lineamientos/datos/02-consistencia-eventual.md) definiendo cuándo usar qué modelo.

---

## Concepto Fundamental

```yaml
# CAP Theorem (Choose 2 of 3)

C - Consistency: All nodes see same data at same time
A - Availability: System responds to every request
P - Partition Tolerance: System works despite network failures

Trade-offs:
  CA (Consistency + Availability):
    - Single-node database (no partitions)
    - Example: Traditional RDBMS on single server
    - ❌ Not partition-tolerant (no distribution)

  CP (Consistency + Partition Tolerance):
    - Strong consistency, may reject requests during partition
    - Example: HBase, MongoDB (default), Consul
    - ⚠️ Sacrifices availability (downtime during network issues)

  AP (Availability + Partition Tolerance):
    - Always available, eventual consistency
    - Example: Cassandra, DynamoDB, Riak
    - ⚠️ Sacrifices consistency (stale reads possible)

Microservices Reality:
  - Distributed by nature → Partition Tolerance REQUIRED
  - Choose: CP (strong consistency) OR AP (high availability)
```

## Strong Consistency

```yaml
# ✅ Strong Consistency (Linearizability)

Definition:
  Once a write completes, ALL subsequent reads see that value

  Timeline:
    t1: Client A writes X = 5 → Write acknowledged
    t2: Client B reads X → Returns 5 ✅
    t3: Client C reads X → Returns 5 ✅

  Guarantee: No stale reads after write completes

Use Cases:

  1. Financial Transactions:
     - Bank account balance
     - Payment processing
     - Reason: Can't show wrong balance (user sees $100, actually $0)

  2. Inventory Management:
     - Stock levels (prevent overselling)
     - Seat reservations (prevent double-booking)
     - Reason: Consistency critical (can't sell item twice)

  3. Configuration Management:
     - Feature flags
     - Security policies
     - Reason: All servers must see same config

Implementation (PostgreSQL with Synchronous Replication):

  # postgresql.conf
  synchronous_commit = on
  synchronous_standby_names = 'standby1, standby2'

  Flow:
    1. Primary receives write (UPDATE accounts SET balance = 100)
    2. Primary writes to WAL
    3. Primary replicates to standby
    4. Standby acknowledges write
    5. Primary acknowledges to client ✅

  Latency: Higher (wait for replication)
  Availability: Lower (if standby down, writes block)
  Consistency: Strong ✅

Implementation (Kafka with acks=all):

  # Producer config
  acks = all  # Wait for all in-sync replicas
  min.insync.replicas = 2  # At least 2 replicas must ack

  Flow:
    1. Producer sends message to topic partition
    2. Leader writes message
    3. Leader waits for followers to replicate
    4. All in-sync replicas acknowledge
    5. Leader acknowledges to producer ✅

  Guarantee: Message durably written to multiple brokers
```

## Eventual Consistency

```yaml
# ✅ Eventual Consistency

Definition:
  If no new updates, eventually all replicas converge to same value

  Timeline (with lag):
    t1: Client A writes X = 5 to Node 1 → Write acknowledged
    t2: Client B reads X from Node 2 → Returns 3 ⚠️ (stale, not replicated yet)
    t3: Replication completes
    t4: Client C reads X from Node 2 → Returns 5 ✅ (now consistent)

  Guarantee: Eventually consistent (not immediately)

Use Cases:

  1. Social Media Posts:
     - Like counts
     - Comment threads
     - Reason: User can tolerate seeing "123 likes" when actual is "125"

  2. Product Catalog:
     - Product descriptions
     - Images
     - Reason: Small delay OK (not transactional)

  3. Analytics/Reporting:
     - Dashboard metrics
     - Sales reports
     - Reason: Real-time not required (batch updates OK)

  4. DNS/CDN:
     - DNS records
     - CDN cache
     - Reason: TTL-based, eventual propagation accepted

Implementation (DynamoDB Eventually Consistent Reads):

  # Default: Eventually consistent read (cheaper, faster)
  response = dynamodb.get_item(
      TableName='Orders',
      Key={'OrderId': 'order-123'},
      ConsistentRead=False  # ✅ Eventually consistent (default)
  )

  Latency: Lower (read from any replica)
  Availability: Higher (any replica can serve)
  Consistency: Eventual ⚠️ (may be stale)

  # Option: Strongly consistent read (more expensive)
  response = dynamodb.get_item(
      TableName='Orders',
      Key={'OrderId': 'order-123'},
      ConsistentRead=True  # ✅ Strongly consistent
  )

  Latency: Higher (read from primary)
  Cost: 2x read capacity units

Implementation (Read Replicas):

  Sales Service:
    - Primary DB (PostgreSQL): Handle writes
    - Read Replica 1: Handle read queries (lag ~2 seconds)
    - Read Replica 2: Handle read queries (lag ~2 seconds)

  Write Flow:
    Client → Service → Primary DB → Acknowledged ✅

  Read Flow:
    Client → Service → Read Replica → Return data

  Consistency: Eventual (replica lag ~2 seconds)
  Benefit: Scale reads horizontally
```

## Consistency Patterns in Talma

```yaml
# ✅ Consistency Model by Use Case

Strong Consistency (CP - Consistency Priority):
  1. Payments:
    Service: Billing Service
    Storage: PostgreSQL (single-region, synchronous replication)
    Reason: Financial data, can't have discrepancies
    Trade-off: Lower availability (downtime during partition)

  2. Inventory:
    Service: Inventory Service
    Storage: PostgreSQL with row-level locks
    Reason: Prevent overselling (stock = 1, can't sell 2)
    Implementation: SELECT * FROM products WHERE product_id = 'P001' FOR UPDATE;
      -- Row locked, other transactions wait
      UPDATE products SET stock = stock - 1 WHERE product_id = 'P001';
      COMMIT; -- Lock released

  3. Authentication:
    Service: Keycloak
    Storage: PostgreSQL
    Reason: User credentials must be consistent (can't have wrong password)

Eventual Consistency (AP - Availability Priority):
  1. Product Catalog:
    Service: Catalog Service
    Storage: DynamoDB (multi-region)
    Reason: Product descriptions, images (not transactional)
    Acceptable: User sees old price for 1-2 seconds during update

  2. Order History (Read Model):
    Service: Sales Service (CQRS read side)
    Storage: ElasticSearch
    Update: Async from Kafka events (OrderCreated, OrderUpdated)
    Reason: Query optimization, eventual consistency OK
    Lag: ~5 seconds from write model

  3. Notifications:
    Service: Notification Service
    Storage: SQS → Lambda → DynamoDB
    Reason: Delivery guarantees (at-least-once), eventual processing
    Acceptable: Email arrives 30 seconds after order placed

Hybrid (Strong Write, Eventual Read):
  1. User Profile:
    Write: PostgreSQL primary (strong consistency)
    Read: Redis cache (TTL 60s, eventual consistency)

    Flow:
      Write: Client → API → PostgreSQL → Cache invalidation
      Read: Client → API → Redis (if miss, fetch from PostgreSQL)

    Consistency:
      - Writes: Strong (PostgreSQL ACID)
      - Reads: Eventual (cache may be stale up to 60s)

    Acceptable: User updates profile, sees old avatar for 60s
```

## Read-After-Write Consistency

```yaml
# ✅ Read-Your-Writes Consistency

Problem:
  User creates order → Redirects to order details page → 404 Not Found
  Reason: Read replica lag (write to primary, read from replica)

Solution 1: Read from Primary for Recent Writes

  public async Task<Order> GetOrderAsync(Guid orderId)
  {
      // ✅ Check if user just created this order (< 5 seconds ago)
      var userId = _currentUser.GetUserId();
      var recentWrite = await _cache.GetAsync($"recent_write:{userId}:{orderId}");

      if (recentWrite != null)
      {
          // ✅ Read from primary (strong consistency)
          return await _primaryDb.GetOrderAsync(orderId);
      }
      else
      {
          // ✅ Read from replica (eventual consistency)
          return await _replicaDb.GetOrderAsync(orderId);
      }
  }

Solution 2: Session Stickiness (Read from Same Replica)

  Load Balancer:
    - Use session cookie to route user to same replica
    - Replica lag is consistent (user doesn't see time travel)

Solution 3: Version-Based Routing

  Write Response:
    HTTP 201 Created
    ETag: "version-123"

  Subsequent Read:
    GET /api/orders/order-123
    If-None-Match: "version-123"

    API checks: Replica has version-123?
      - Yes → Return from replica
      - No → Read from primary (ensure consistency)

Solution 4: Retry with Backoff

  try {
    order = await GetOrderFromReplica(orderId);
  } catch (NotFoundException) {
    await Task.Delay(1000); // Wait for replication
    order = await GetOrderFromPrimary(orderId); // Retry from primary
  }
```

## Conflict Resolution (Eventual Consistency)

```yaml
# ✅ Handling Conflicts in Eventual Consistency

Scenario: Two Users Update Same Record Simultaneously

  t1: User A reads product price = $100 (from Replica 1)
  t2: User B reads product price = $100 (from Replica 2)
  t3: User A updates price = $90 (writes to Primary)
  t4: User B updates price = $95 (writes to Primary)

  Conflict: Both based on $100, which update wins?

Strategy 1: Last-Write-Wins (LWW)

  Primary receives:
    - User A: price = $90 at t3 (timestamp: 1706457600)
    - User B: price = $95 at t4 (timestamp: 1706457601)

  Result: User B wins (latest timestamp)

  Implementation:
    UPDATE products
    SET price = $95, updated_at = 1706457601
    WHERE product_id = 'P001'
      AND updated_at < 1706457601; -- Only if newer

  Downside: User A's update lost (no notification)

Strategy 2: Version Vectors

  Each write includes version:
    User A: price = $90, version = 1
    User B: price = $95, version = 1 (conflict detected)

  Result: Primary detects conflict (both version 1)

  Resolution:
    - Return 409 Conflict to User B
    - User B refetches price ($90), re-applies change
    - User B retries: price = $95, version = 2 ✅

Strategy 3: Application-Level Merge

  Example: Shopping Cart

  User A adds: [Item1, Item2]
  User B adds: [Item3]

  Conflict: Both modified cart simultaneously

  Resolution: Merge (union)
    Final cart: [Item1, Item2, Item3] ✅

  Implementation:
    - Store cart as set (not overwrite)
    - Merge on read (combine all versions)

Strategy 4: Operational Transformation (OT)

  Example: Collaborative Document Editing

  User A inserts "Hello" at position 0
  User B inserts "World" at position 0

  Conflict: Both insert at position 0

  Resolution: Transform operations
    - User A's op executes first: "Hello"
    - User B's op transformed: insert at position 5 → "HelloWorld"

  Used by: Google Docs, Figma
```

## Monitoring Consistency Lag

```yaml
# ✅ Monitor Replication Lag

PostgreSQL Read Replica Lag:

  # Query on primary
  SELECT
    client_addr AS replica_ip,
    state,
    sync_state,
    replay_lag,
    write_lag
  FROM pg_stat_replication;

  # Result
  replica_ip      | state     | sync_state | replay_lag | write_lag
  10.0.20.10      | streaming | async      | 00:00:02   | 00:00:01

  # Alert if lag > 10 seconds

  CloudWatch Alarm:
    Metric: ReplicaLag
    Threshold: > 10 seconds
    Action: Page on-call (investigate replication issue)

DynamoDB Global Tables Replication Lag:

  aws dynamodb describe-table --table-name Orders

  "GlobalTableVersion": "2019.11.21",
  "ReplicationLatencyInMilliseconds": 850

  # Alert if > 5 seconds

Kafka Consumer Lag:

  kafka-consumer-groups --bootstrap-server kafka:9092 \
    --describe --group sales-consumer

  GROUP           TOPIC     PARTITION  LAG
  sales-consumer  orders    0          1250  # 1250 messages behind

  # Alert if lag > 1000

Application Metric:

  # Custom metric: Time between write and read consistency

  await WriteOrder(order); // t1 = 12:00:00.000
  var order = await ReadOrder(orderId); // t2 = 12:00:02.500

  consistencyLag = t2 - t1 = 2.5 seconds

  cloudwatch.PutMetric("ConsistencyLag", 2.5, Unit.Seconds);

  # Target: < 5 seconds
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** usar strong consistency para datos financieros (payments, balances)
- **MUST** usar strong consistency para inventory (prevent overselling)
- **MUST** documentar consistency model por servicio (README)
- **MUST** monitorear replication lag (alert if > 10s)
- **MUST** implementar conflict resolution (eventual consistency)

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar eventual consistency para read-heavy workloads (catalog)
- **SHOULD** implementar read-after-write consistency (user sees own writes)
- **SHOULD** usar CQRS para separar read/write models
- **SHOULD** usar cache with TTL (eventual consistency OK)

### MUST NOT (Prohibido)

- **MUST NOT** usar eventual consistency para financial data
- **MUST NOT** assume immediate consistency en sistemas distribuidos
- **MUST NOT** ignore replication lag (monitor and alert)
- **MUST NOT** use strong consistency everywhere (performance cost)

---

## Referencias

- [Lineamiento: Consistencia Eventual](../../lineamientos/datos/02-consistencia-eventual.md)
- [Saga Pattern](./saga-pattern.md)
- [CQRS Pattern](./cqrs-pattern.md)
- [Transactional Outbox](../../guias-arquitectura/transactional-outbox.md)
- [Database Per Service](./database-per-service.md)
